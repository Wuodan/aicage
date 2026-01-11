from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from aicage.config._yaml import expect_string
from aicage.config.errors import ConfigError
from aicage.config.resources import find_packaged_path

_EXTENSION_SCHEMA_PATH = "validation/extension.schema.json"
_EXTENSION_CONTEXT = "extension metadata"


def validate_extension_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    context = _EXTENSION_CONTEXT
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

    for key, value in mapping.items():
        schema_entry = properties.get(key)
        if schema_entry is None:
            continue
        _validate_value(value, schema_entry, f"{context}.{key}")

    return dict(mapping)


@lru_cache(maxsize=1)
def _load_schema() -> dict[str, Any]:
    path = find_packaged_path(_EXTENSION_SCHEMA_PATH)
    payload = path.read_text(encoding="utf-8")
    return json.loads(payload)


def _validate_value(value: Any, schema_entry: dict[str, Any], context: str) -> None:
    schema_type = schema_entry.get("type")
    if schema_type == "string":
        expect_string(value, context)
        return
    raise ConfigError(f"{context} has unsupported schema type '{schema_type}'.")
