from __future__ import annotations

from pathlib import Path

from aicage.paths import IMAGE_EXTENDED_BUILD_LOG_DIR
from aicage.registry._sanitize import sanitize
from aicage.registry._time import timestamp


def build_log_path_for_image(image_ref: str) -> Path:
    return IMAGE_EXTENDED_BUILD_LOG_DIR / f"{sanitize(image_ref)}-{timestamp()}.log"
