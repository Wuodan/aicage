from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

_DEFAULT_STATE_DIR = "~/.aicage/state/local-build"


@dataclass(frozen=True)
class _BuildRecord:
    agent: str
    base: str
    agent_version: str
    base_image: str
    base_digest: str | None
    image_ref: str
    built_at: str


class _BuildStore:
    def __init__(self, base_dir: Path | None = None) -> None:
        self._base_dir = base_dir or Path(os.path.expanduser(_DEFAULT_STATE_DIR))

    def load(self, agent: str, base: str) -> _BuildRecord | None:
        path = self._path(agent, base)
        if not path.is_file():
            return None
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(payload, dict):
            return None
        base_digest = payload.get("base_digest")
        return _BuildRecord(
            agent=str(payload.get("agent", "")),
            base=str(payload.get("base", "")),
            agent_version=str(payload.get("agent_version", "")),
            base_image=str(payload.get("base_image", "")),
            base_digest=str(base_digest) if base_digest is not None else None,
            image_ref=str(payload.get("image_ref", "")),
            built_at=str(payload.get("built_at", "")),
        )

    def save(self, record: _BuildRecord) -> Path:
        self._base_dir.mkdir(parents=True, exist_ok=True)
        path = self._path(record.agent, record.base)
        payload = {
            "agent": record.agent,
            "base": record.base,
            "agent_version": record.agent_version,
            "base_image": record.base_image,
            "base_digest": record.base_digest,
            "image_ref": record.image_ref,
            "built_at": record.built_at,
        }
        path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")
        return path

    def _path(self, agent: str, base: str) -> Path:
        filename = f"{_sanitize(agent)}-{base}.yaml"
        return self._base_dir / filename


def _sanitize(value: str) -> str:
    return value.replace("/", "_")
