# Polyglot Agentic Coding Base Image (Debian)

This document defines a **practical, agent‑friendly toolset** for Debian‑based Docker images used for *agentic coding*. The focus is on **real‑world buildability**, not IDE convenience.

The guiding principles:
- Agents must be able to **build, test, and debug** arbitrary repositories
- Prefer **ecosystem‑native tooling** over distro shortcuts
- Avoid baking unnecessary runtime variants unless required

---

## 1. Core Base (Already Present)

Baseline utilities required for almost all projects:

```bash
apt-get install -y --no-install-recommends \
  bash \
  bash-completion \
  build-essential \
  ca-certificates \
  curl \
  git \
  gnupg \
  jq \
  locales \
  nano \
  openssh-client \
  pipx \
  python3 \
  python3-pip \
  python3-venv \
  gosu \
  ripgrep \
  tar \
  tini \
  unzip \
  xz-utils \
  zip
```

Recommended locale fix:

```bash
apt-get install -y locales-all
```

---

## 2. Java Ecosystem

### Required

```bash
openjdk-21-jdk   # or openjdk-17-jdk (LTS conservative)
maven
gradle
```

### Common Extras

```bash
ant
protobuf-compiler
```

### Native Dependencies (frequently needed)

```bash
libssl-dev
zlib1g-dev
```

### Optional: Multi‑JDK Support

Use SDKMAN (installed via curl, not apt) to allow agents to switch Java versions per project.

---

## 3. C / C++ Toolchain

### Baseline (partially covered by build-essential)

```bash
build-essential
```

### Modern Build & Debug Stack

```bash
cmake
ninja-build
pkg-config
gdb
```

### Strongly Recommended

```bash
clang
lld
lldb
```

### Diagnostics & Profiling (Optional)

```bash
valgrind
strace
ltrace
```

---

## 4. Rust

### Correct Installation Method

Rust should **not** be installed via apt.

```bash
curl https://sh.rustup.rs | sh -s -- -y
```

This installs:
- rustc
- cargo
- rustfmt
- clippy

### Required System Dependencies

```bash
pkg-config
libssl-dev
```

Without these, many crates will fail to compile.

---

## 5. Python (Extended)

Already present:
- python3
- pip
- venv
- pipx

### Required for Native Extensions

```bash
python3-dev
```

### Optional

```bash
pipx install tox
```

---

## 6. Node.js Ecosystem

Besides Node.js itself, agents frequently need multiple package managers.

```bash
npm
yarn
pnpm
```

Preferred approach (Node ≥16):

```bash
corepack enable
```

---

## 7. Go

Go tooling appears frequently in infra and tooling repositories.

```bash
golang
```

Common use cases:
- Kubernetes tools
- Terraform helpers
- GitHub / CI utilities

---

## 8. .NET (Optional, Enterprise)

Only include if required by your target repos.

```bash
dotnet-sdk-8.0
```

Requires Microsoft package repositories.

---

## 9. Universal Build & Agent Utilities

These appear constantly in CI scripts and build systems:

```bash
make
file
patch
rsync
tree
less
procps
time
```

Networking & debugging:

```bash
iproute2
dnsutils
netcat-openbsd
```

Archive formats you *will* encounter:

```bash
p7zip-full
```

---

## 10. Container / Infra Tooling (Optional)

Only if agents build or inspect images:

```bash
skopeo
buildah
podman
```

---

## 11. Recommended Layering Strategy

Instead of one monolithic image, split logically:

- **core** – shell, git, curl, jq, python base
- **native** – C/C++ + Rust toolchains
- **managed** – Java, Node, Python extras, Go
- **infra** – container and CI helpers

This keeps images maintainable while preserving agent flexibility.

---

## Summary

What matters for agentic coding images is **ecosystem completeness**, not tool count:

- Java ⇒ JDK + Maven + Gradle
- C/C++ ⇒ CMake + Ninja + Clang + GDB
- Rust ⇒ rustup + libssl-dev
- Python ⇒ python3-dev
- Go ⇒ golang
- Glue ⇒ pkg-config, rsync, patch

This baseline supports the majority of modern open‑source and enterprise repositories without surprise build failures.

