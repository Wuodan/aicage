from __future__ import annotations

from pathlib import Path
from typing import Any

from aicage.config._schema_validation import load_schema, validate_schema_mapping
from aicage.config._yaml import expect_bool, expect_string
from aicage.config.errors import ConfigError
from aicage.config.images_metadata.models import BUILD_LOCAL_KEY

_AGENT_SCHEMA_PATH = "validation/agent.schema.json"
_CUSTOM_AGENT_CONTEXT = "custom agent metadata"


def validate_agent_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    context = _CUSTOM_AGENT_CONTEXT
    schema = load_schema(_AGENT_SCHEMA_PATH)
    return validate_schema_mapping(
        mapping,
        schema,
        context,
        normalizer=_apply_defaults,
        value_validator=_validate_value,
    )


def ensure_required_files(agent_name: str, agent_dir: Path) -> None:
    missing = [name for name in ("install.sh", "version.sh") if not (agent_dir / name).is_file()]
    if missing:
        raise ConfigError(f"Custom agent '{agent_name}' is missing {', '.join(missing)}.")


def _apply_defaults(mapping: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(mapping)
    normalized.setdefault(BUILD_LOCAL_KEY, True)
    return normalized


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
