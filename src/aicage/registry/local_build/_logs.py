from __future__ import annotations

import os
from pathlib import Path

from aicage.registry._sanitize import sanitize
from aicage.registry._time import timestamp

_DEFAULT_LOG_DIR = "~/.aicage/logs/build"


def build_log_path(agent: str, base: str) -> Path:
    log_dir = Path(os.path.expanduser(_DEFAULT_LOG_DIR))
    return log_dir / f"{sanitize(agent)}-{base}-{timestamp()}.log"
