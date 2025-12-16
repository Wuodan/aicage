from pathlib import Path

__all__ = ["default_ssh_dir"]


def default_ssh_dir() -> Path:
    return Path.home() / ".ssh"
