from pathlib import Path

from .errors import ConfigError

__all__ = ["find_packaged_path"]


def find_packaged_path(filename: str) -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "config" / filename
        if candidate.is_file():
            return candidate
    raise ConfigError(f"Packaged config file '{filename}' was not found.")
