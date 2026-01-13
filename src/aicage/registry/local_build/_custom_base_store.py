from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from aicage import paths as paths_module
from aicage.registry._sanitize import sanitize

_BASE_KEY: str = "base"
_FROM_IMAGE_KEY: str = "from_image"
_FROM_IMAGE_DIGEST_KEY: str = "from_image_digest"
_IMAGE_REF_KEY: str = "image_ref"
_BUILT_AT_KEY: str = "built_at"


@dataclass(frozen=True)
class CustomBaseBuildRecord:
    base: str
    from_image: str
    from_image_digest: str
    image_ref: str
    built_at: str


class CustomBaseBuildStore:
    def __init__(self) -> None:
        self._base_dir = paths_module.BASE_IMAGE_BUILD_STATE_DIR

    def load(self, base: str) -> CustomBaseBuildRecord | None:
        path = self._path(base)
        if not path.is_file():
            return None
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(payload, dict):
            return None
        return CustomBaseBuildRecord(
            base=str(payload.get(_BASE_KEY, "")),
            from_image=str(payload.get(_FROM_IMAGE_KEY, "")),
            from_image_digest=str(payload.get(_FROM_IMAGE_DIGEST_KEY, "")),
            image_ref=str(payload.get(_IMAGE_REF_KEY, "")),
            built_at=str(payload.get(_BUILT_AT_KEY, "")),
        )

    def save(self, record: CustomBaseBuildRecord) -> Path:
        self._base_dir.mkdir(parents=True, exist_ok=True)
        path = self._path(record.base)
        payload = {
            _BASE_KEY: record.base,
            _FROM_IMAGE_KEY: record.from_image,
            _FROM_IMAGE_DIGEST_KEY: record.from_image_digest,
            _IMAGE_REF_KEY: record.image_ref,
            _BUILT_AT_KEY: record.built_at,
        }
        path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")
        return path

    def _path(self, base: str) -> Path:
        filename = f"base-{sanitize(base)}.yaml"
        return self._base_dir / filename
