from __future__ import annotations

import os
from pathlib import Path

from ._sanitize import sanitize
from ._time import timestamp

_DEFAULT_LOG_DIR = "~/.aicage/logs/pull"


def pull_log_path(image_ref: str) -> Path:
    log_dir = Path(os.path.expanduser(_DEFAULT_LOG_DIR))
    return log_dir / f"{sanitize(image_ref)}-{timestamp()}.log"
