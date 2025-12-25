import subprocess
from pathlib import Path

__all__ = ["capture_stdout"]


def capture_stdout(command: list[str], cwd: Path | None = None) -> str | None:
    try:
        result = subprocess.run(
            command, check=True, capture_output=True, text=True, cwd=str(cwd) if cwd else None
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return result.stdout
