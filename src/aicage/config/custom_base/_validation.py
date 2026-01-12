from __future__ import annotations

from typing import Any

from aicage.config._schema_validation import load_schema, validate_schema_mapping
from aicage.config._yaml import expect_string
from aicage.config.errors import ConfigError

_CUSTOM_BASE_SCHEMA_PATH: str = "validation/base.schema.json"
_CUSTOM_BASE_CONTEXT: str = "custom base metadata"


def validate_base_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    schema = load_schema(_CUSTOM_BASE_SCHEMA_PATH)
    return validate_schema_mapping(
        mapping,
        schema,
        _CUSTOM_BASE_CONTEXT,
        value_validator=_validate_value,
    )


def _validate_value(value: Any, schema_entry: dict[str, Any], context: str) -> None:
    schema_type = schema_entry.get("type")
    if schema_type == "string":
        expect_string(value, context)
        return
    raise ConfigError(f"{context} has unsupported schema type '{schema_type}'.")
