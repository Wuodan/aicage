from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from aicage.paths import DEFAULT_VERSION_CHECK_STATE_DIR

_AGENT_KEY: str = "agent"
_VERSION_KEY: str = "version"
_CHECKED_AT_KEY: str = "checked_at"


class VersionCheckStore:
    def __init__(self, base_dir: Path | None = None) -> None:
        self._base_dir = base_dir or DEFAULT_VERSION_CHECK_STATE_DIR.expanduser()

    def save(self, agent: str, version: str) -> Path:
        self._base_dir.mkdir(parents=True, exist_ok=True)
        path = self._base_dir / f"{_sanitize_agent_name(agent)}.yaml"
        with path.open("w", encoding="utf-8") as handle:
            payload = {
                _AGENT_KEY: agent,
                _VERSION_KEY: version,
                _CHECKED_AT_KEY: _now_iso(),
            }
            yaml.safe_dump(payload, handle, sort_keys=True)
        return path


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize_agent_name(agent_name: str) -> str:
    return agent_name.replace("/", "_")
