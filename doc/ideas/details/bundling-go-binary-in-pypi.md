# Shipping a Go binary inside a PyPI package (and using it)

This is the common pattern: **build platform-specific wheels**, each wheel **contains the right Go executable**, and 
your Python code finds and runs it via `subprocess`.

## Key idea

- PyPI packages are **cross-platform only if you ship wheels per platform**.
- A Go binary is platform-specific (linux/mac/windows, amd64/arm64, libc).
- So you publish multiple wheels:
  - `manylinux_*` (glibc Linux)
  - `musllinux_*` (Alpine)
  - `macosx_*`
  - `win_amd64` / `win_arm64`

## Minimal project layout

```
yourpkg/
  pyproject.toml
  src/yourpkg/
    __init__.py
    _bin/
      .keep
    _tool.py
```

You will place the built binary into `src/yourpkg/_bin/<platform>/tool[.exe]` during wheel build.

Example convention:

```
src/yourpkg/_bin/linux_amd64/tool
src/yourpkg/_bin/linux_arm64/tool
src/yourpkg/_bin/macos_arm64/tool
src/yourpkg/_bin/windows_amd64/tool.exe
```

## Build the Go binary during wheel builds

### Recommended: `cibuildwheel` (CI) + a build script

`cibuildwheel` builds wheels in isolated environments for each target.

In GitHub Actions, you typically:

1. Checkout
2. Install Go
3. Build your Go tool for the wheel’s platform
4. Copy it into `src/yourpkg/_bin/...`
5. Build wheel
6. Upload to PyPI

### Cross-compiling vs native compiling

- **Linux manylinux** wheels are easiest if you build inside manylinux containers (what `cibuildwheel` already does).
- For Alpine (`musllinux`), build in musllinux environment.
- For macOS/Windows, build on runners.
- Go cross-compiles well, but **CGO** and libc targets can complicate things; prefer native builds per runner unless 
- you know you’re fully static.

## Packaging config

### Option A: setuptools (simple, widely used)

`pyproject.toml` (sketch)

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "yourpkg"
version = "0.1.0"
requires-python = ">=3.9"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.package-data]
"yourpkg" = ["_bin/**"]
```

This includes your binary files inside the wheel.

### Option B: hatchling (also good)

You can include package data similarly via hatch configuration. (Setuptools is easiest if you’re already using it.)

## Runtime: locating and executing the bundled binary

Don’t assume a file-system path to package resources. Use `importlib.resources`.

### Example: pick a binary path by platform

```python
import os
import platform
import stat
import subprocess
from importlib import resources

def _platform_tag() -> str:
    sys = platform.system().lower()
    machine = platform.machine().lower()

    # Normalize arch names
    if machine in ("x86_64", "amd64"):
        arch = "amd64"
    elif machine in ("aarch64", "arm64"):
        arch = "arm64"
    else:
        raise RuntimeError(f"Unsupported arch: {machine}")

    if sys.startswith("linux"):
        # If you care about musllinux vs manylinux, detect musl here.
        # Many projects ship only manylinux and skip Alpine, or ship both.
        return f"linux_{arch}"
    if sys.startswith("darwin"):
        return f"macos_{arch}"
    if sys.startswith("windows"):
        return f"windows_{arch}"
    raise RuntimeError(f"Unsupported OS: {sys}")

def _binary_name() -> str:
    return "tool.exe" if platform.system().lower().startswith("windows") else "tool"

def tool_path() -> str:
    tag = _platform_tag()
    name = _binary_name()
    rel = f"_bin/{tag}/{name}"

    # resources.files returns a Traversable; as_file gives a real path
    r = resources.files("yourpkg").joinpath(rel)
    if not r.is_file():
        raise FileNotFoundError(f"Bundled tool not found: {rel}")

    # If the package is in a zip, as_file extracts to a temp location
    ctx = resources.as_file(r)
    p = ctx.__enter__()  # manage with a context manager in real code

    # Ensure executable bit on POSIX
    if os.name == "posix":
        mode = os.stat(p).st_mode
        os.chmod(p, mode | stat.S_IXUSR)

    return str(p), ctx  # return ctx so caller can __exit__ later

def run_tool(args: list[str]) -> subprocess.CompletedProcess:
    p, ctx = tool_path()
    try:
        return subprocess.run([p, *args], check=True, text=True, capture_output=True)
    finally:
        ctx.__exit__(None, None, None)
```

Notes:
- `resources.as_file()` is important because wheels can be installed in ways where resources aren’t directly on disk.
- You must manage the context properly; in production, wrap it with `with resources.as_file(...) as p:`.

## How to build + copy the binary during wheel builds

### A practical pattern

- Put the Go source in `go/` (or a separate repo).
- During build, produce `tool` and copy it into `src/yourpkg/_bin/<tag>/`.

Example build command (Linux runner):

```bash
mkdir -p src/yourpkg/_bin/linux_amd64
go build -trimpath -ldflags="-s -w" -o src/yourpkg/_bin/linux_amd64/tool ./go/cmd/tool
```

Windows:

```powershell
mkdir src\yourpkg\_bin\windows_amd64 -Force
go build -trimpath -ldflags="-s -w" -o src\yourpkg\_bin\windows_amd64\tool.exe .\go\cmd\tool
```

## Versioning & reproducibility

- Embed version in the Go binary using `-ldflags "-X main.version=..."`.
- Keep Go module dependencies pinned.
- Consider `-trimpath` and `-buildvcs=false` for reproducible builds.

## Gotchas

- **Alpine**: if your Go binary uses CGO or dynamic linking, you may need a musl build and must publish `musllinux_*` 
  wheels. Pure-Go static binaries are easiest.
- **Code signing / notarization**: macOS may warn on downloaded binaries; inside wheels it’s typically fine, but 
  enterprise setups may be strict.
- **Antivirus**: shipping executables in Python wheels can trigger scanning; keep it minimal and transparent.
- **Licensing**: you’re redistributing a compiled artifact; ensure licenses are compatible and included.

## When you should NOT bundle the binary

- If users already have the tool installed and you can depend on it (simpler).
- If the binary is huge and inflates wheels.
- If you need frequent binary updates independent of Python release cadence.

## A simple alternative: “download on first run”

Some projects ship Python-only wheels and download the right binary on first use.
Pros: smaller wheels.
Cons: network, trust, caching, corporate proxies.

For CI/dev-tooling use-cases, bundling in wheels is usually the smoother UX.
