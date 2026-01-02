from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from ._store import sanitize

_DEFAULT_LOG_DIR = "~/.aicage/logs/build"


def build_log_path(agent: str, base: str) -> Path:
    log_dir = Path(os.path.expanduser(_DEFAULT_LOG_DIR))
    return log_dir / f"{sanitize(agent)}-{base}-{_timestamp()}.log"


def pull_log_path(agent: str, base: str) -> Path:
    log_dir = Path(os.path.expanduser(_DEFAULT_LOG_DIR))
    return log_dir / f"{sanitize(agent)}-{base}-pull-{_timestamp()}.log"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
