from pathlib import Path
from typing import Any

import yaml

from aicage.config.errors import ConfigError


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        payload = path.read_text(encoding="utf-8")
        data = yaml.safe_load(payload) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigError(f"Failed to read YAML from {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"YAML at {path} must be a mapping.")
    return data
