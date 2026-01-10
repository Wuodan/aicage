from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from aicage.config._yaml import expect_bool, expect_string
from aicage.config.errors import ConfigError
from aicage.config.images_metadata.models import BUILD_LOCAL_KEY
from aicage.config.resources import find_packaged_path

_AGENT_SCHEMA_PATH = "validation/agent.schema.json"
_CUSTOM_AGENT_CONTEXT = "custom agent metadata"


def validate_agent_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    context = _CUSTOM_AGENT_CONTEXT
    if not isinstance(mapping, dict):
        raise ConfigError(f"{context} must be a mapping.")

    schema = _load_schema()
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    additional = schema.get("additionalProperties", True)

    missing = sorted(required - set(mapping))
    if missing:
        raise ConfigError(f"{context} missing required keys: {', '.join(missing)}.")

    if additional is False:
        unknown = sorted(set(mapping) - set(properties))
        if unknown:
            raise ConfigError(f"{context} contains unsupported keys: {', '.join(unknown)}.")

    normalized = dict(mapping)
    normalized.setdefault(BUILD_LOCAL_KEY, True)

    for key, value in normalized.items():
        schema_entry = properties.get(key)
        if schema_entry is None:
            continue
        _validate_value(value, schema_entry, f"{context}.{key}")

    return normalized


def ensure_required_files(agent_name: str, agent_dir: Path) -> None:
    missing = [name for name in ("install.sh", "version.sh") if not (agent_dir / name).is_file()]
    if missing:
        raise ConfigError(f"Custom agent '{agent_name}' is missing {', '.join(missing)}.")


@lru_cache(maxsize=1)
def _load_schema() -> dict[str, Any]:
    path = find_packaged_path(_AGENT_SCHEMA_PATH)
    payload = path.read_text(encoding="utf-8")
    return json.loads(payload)


def _validate_value(value: Any, schema_entry: dict[str, Any], context: str) -> None:
    schema_type = schema_entry.get("type")
    if schema_type == "string":
        expect_string(value, context)
        return
    if schema_type == "boolean":
        expect_bool(value, context)
        return
    if schema_type == "array":
        _expect_str_list(value, context, schema_entry)
        return
    raise ConfigError(f"{context} has unsupported schema type '{schema_type}'.")


def _expect_str_list(value: Any, context: str, schema_entry: dict[str, Any]) -> None:
    if not isinstance(value, list):
        raise ConfigError(f"{context} must be a list.")
    item_schema = schema_entry.get("items", {})
    item_type = item_schema.get("type")
    if item_type != "string":
        raise ConfigError(f"{context} items must be strings.")
    for item in value:
        expect_string(item, context)
