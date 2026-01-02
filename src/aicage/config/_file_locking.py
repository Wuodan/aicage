from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import portalocker

from aicage.config.errors import ConfigError

_LOCK_TIMEOUT_SECONDS = 30


@contextmanager
def lock_project_config(project_config_path: Path) -> Iterator[None]:
    try:
        with _lock_file(project_config_path):
            yield
    except portalocker.exceptions.LockException as exc:  # pragma: no cover - rare file lock failure
        raise ConfigError(f"Failed to lock project configuration file: {exc}") from exc


def _lock_file(path: Path) -> portalocker.Lock:
    path.parent.mkdir(parents=True, exist_ok=True)
    return portalocker.Lock(str(path), timeout=_LOCK_TIMEOUT_SECONDS, mode="a+")
