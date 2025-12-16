from pathlib import Path

from ._exec import _capture_stdout

__all__ = ["resolve_gpg_home"]


def resolve_gpg_home() -> Path | None:
    stdout = _capture_stdout(["gpgconf", "--list-dirs", "homedir"])
    if not stdout:
        return None
    path = stdout.strip()
    return Path(path).expanduser() if path else None
