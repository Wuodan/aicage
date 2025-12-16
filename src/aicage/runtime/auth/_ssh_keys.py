from pathlib import Path


def default_ssh_dir() -> Path:
    return Path.home() / ".ssh"
