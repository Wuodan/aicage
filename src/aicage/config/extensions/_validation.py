from __future__ import annotations

from typing import Any

from aicage.config._schema_validation import load_schema, validate_schema_mapping
from aicage.config._yaml import expect_string
from aicage.config.errors import ConfigError

_EXTENSION_SCHEMA_PATH = "validation/extension.schema.json"
_EXTENSION_CONTEXT = "extension metadata"


def validate_extension_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    context = _EXTENSION_CONTEXT
    schema = load_schema(_EXTENSION_SCHEMA_PATH)
    return validate_schema_mapping(mapping, schema, context, value_validator=_validate_value)


def _validate_value(value: Any, schema_entry: dict[str, Any], context: str) -> None:
    schema_type = schema_entry.get("type")
    if schema_type == "string":
        expect_string(value, context)
        return
    raise ConfigError(f"{context} has unsupported schema type '{schema_type}'.")
