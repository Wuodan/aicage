from __future__ import annotations

from pathlib import Path

from ..paths import IMAGE_PULL_LOG_DIR
from ._sanitize import sanitize
from ._time import timestamp


def pull_log_path(image_ref: str) -> Path:
    return IMAGE_PULL_LOG_DIR / f"{sanitize(image_ref)}-{timestamp()}.log"
