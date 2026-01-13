from __future__ import annotations

from pathlib import Path

import yaml

from aicage import paths as paths_module
from aicage.registry._time import now_iso

_AGENT_KEY: str = "agent"
_VERSION_KEY: str = "version"
_CHECKED_AT_KEY: str = "checked_at"


class VersionCheckStore:
    def __init__(self) -> None:
        self._base_dir = paths_module.AGENT_VERSION_CHECK_STATE_DIR

    def save(self, agent: str, version: str) -> Path:
        self._base_dir.mkdir(parents=True, exist_ok=True)
        path = self._base_dir / f"{_sanitize_agent_name(agent)}.yaml"
        with path.open("w", encoding="utf-8") as handle:
            payload = {
                _AGENT_KEY: agent,
                _VERSION_KEY: version,
                _CHECKED_AT_KEY: now_iso(),
            }
            yaml.safe_dump(payload, handle, sort_keys=True)
        return path


def _sanitize_agent_name(agent_name: str) -> str:
    return agent_name.replace("/", "_")
