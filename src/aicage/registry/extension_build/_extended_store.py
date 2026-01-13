from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from aicage import paths as paths_module
from aicage._lists import read_str_list_or_empty
from aicage.registry._sanitize import sanitize

_AGENT_KEY: str = "agent"
_BASE_KEY: str = "base"
_IMAGE_REF_KEY: str = "image_ref"
_EXTENSIONS_KEY: str = "extensions"
_EXTENSION_HASH_KEY: str = "extension_hash"
_BASE_IMAGE_KEY: str = "base_image"
_BUILT_AT_KEY: str = "built_at"


@dataclass(frozen=True)
class ExtendedBuildRecord:
    agent: str
    base: str
    image_ref: str
    extensions: list[str]
    extension_hash: str
    base_image: str
    built_at: str


class ExtendedBuildStore:
    def __init__(self) -> None:
        self._base_dir = paths_module.IMAGE_EXTENDED_BUILD_STATE_DIR

    def load(self, image_ref: str) -> ExtendedBuildRecord | None:
        path = self._path(image_ref)
        if not path.is_file():
            return None
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(payload, dict):
            return None
        return ExtendedBuildRecord(
            agent=str(payload.get(_AGENT_KEY, "")),
            base=str(payload.get(_BASE_KEY, "")),
            image_ref=str(payload.get(_IMAGE_REF_KEY, "")),
            extensions=read_str_list_or_empty(payload.get(_EXTENSIONS_KEY)),
            extension_hash=str(payload.get(_EXTENSION_HASH_KEY, "")),
            base_image=str(payload.get(_BASE_IMAGE_KEY, "")),
            built_at=str(payload.get(_BUILT_AT_KEY, "")),
        )

    def save(self, record: ExtendedBuildRecord) -> Path:
        self._base_dir.mkdir(parents=True, exist_ok=True)
        path = self._path(record.image_ref)
        payload = {
            _AGENT_KEY: record.agent,
            _BASE_KEY: record.base,
            _IMAGE_REF_KEY: record.image_ref,
            _EXTENSIONS_KEY: list(record.extensions),
            _EXTENSION_HASH_KEY: record.extension_hash,
            _BASE_IMAGE_KEY: record.base_image,
            _BUILT_AT_KEY: record.built_at,
        }
        path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")
        return path

    def _path(self, image_ref: str) -> Path:
        filename = f"{sanitize(image_ref)}.yaml"
        return self._base_dir / filename
