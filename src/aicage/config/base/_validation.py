from typing import Any

from aicage.config._schema_validation import load_schema, validate_schema_mapping
from aicage.config._yaml import expect_bool, expect_string
from aicage.config.base.models import BUILD_LOCAL_KEY
from aicage.config.errors import ConfigError

_BASE_SCHEMA_PATH: str = "validation/base.schema.json"
_BASE_CONTEXT: str = "base metadata"


def validate_base_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    schema = load_schema(_BASE_SCHEMA_PATH)
    return validate_schema_mapping(
        mapping,
        schema,
        _BASE_CONTEXT,
        normalizer=_apply_defaults,
        value_validator=_validate_value,
    )


def _apply_defaults(mapping: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(mapping)
    normalized.setdefault(BUILD_LOCAL_KEY, False)
    return normalized


def _validate_value(value: Any, schema_entry: dict[str, Any], context: str) -> None:
    schema_type = schema_entry.get("type")
    if schema_type == "string":
        expect_string(value, context)
        return
    if schema_type == "boolean":
        expect_bool(value, context)
        return
    raise ConfigError(f"{context} has unsupported schema type '{schema_type}'.")
