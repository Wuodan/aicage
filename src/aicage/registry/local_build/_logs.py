from __future__ import annotations

from pathlib import Path

from aicage.paths import BASE_IMAGE_BUILD_LOG_DIR, IMAGE_BUILD_LOG_DIR
from aicage.registry._sanitize import sanitize
from aicage.registry._time import timestamp


def build_log_path(agent: str, base: str) -> Path:
    return IMAGE_BUILD_LOG_DIR / f"{sanitize(agent)}-{base}-{timestamp()}.log"


def custom_base_log_path(base: str) -> Path:
    return BASE_IMAGE_BUILD_LOG_DIR / f"{sanitize(base)}-{timestamp()}.log"
