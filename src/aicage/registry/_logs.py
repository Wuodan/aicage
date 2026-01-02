from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

_DEFAULT_LOG_DIR = "~/.aicage/logs/pull"


def pull_log_path(image_ref: str) -> Path:
    log_dir = Path(os.path.expanduser(_DEFAULT_LOG_DIR))
    return log_dir / f"{_sanitize(image_ref)}-{_timestamp()}.log"


def _sanitize(value: str) -> str:
    return value.replace("/", "_").replace(":", "_")


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
