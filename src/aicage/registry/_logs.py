from __future__ import annotations

from pathlib import Path

from ._sanitize import sanitize
from ._time import timestamp
from ..paths import IMAGE_PULL_LOG_DIR


def pull_log_path(image_ref: str) -> Path:
    return IMAGE_PULL_LOG_DIR / f"{sanitize(image_ref)}-{timestamp()}.log"
