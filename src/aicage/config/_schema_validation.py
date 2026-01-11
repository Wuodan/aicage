from __future__ import annotations

import json
from collections.abc import Callable
from functools import lru_cache
from typing import Any

from aicage.config.errors import ConfigError
from aicage.config.resources import find_packaged_path

_SchemaValidator = Callable[[Any, dict[str, Any], str], None]
_Normalizer = Callable[[dict[str, Any]], dict[str, Any]]


@lru_cache(maxsize=1)
def load_schema(path: str) -> dict[str, Any]:
    payload = find_packaged_path(path).read_text(encoding="utf-8")
    return json.loads(payload)


def validate_schema_mapping(
    mapping: dict[str, Any],
    schema: dict[str, Any],
    context: str,
    *,
    normalizer: _Normalizer | None = None,
    value_validator: _SchemaValidator | None = None,
) -> dict[str, Any]:
    if not isinstance(mapping, dict):
        raise ConfigError(f"{context} must be a mapping.")

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
    if normalizer is not None:
        normalized = normalizer(normalized)

    if value_validator is not None:
        for key, value in normalized.items():
            schema_entry = properties.get(key)
            if schema_entry is None:
                continue
            value_validator(value, schema_entry, f"{context}.{key}")

    return normalized
