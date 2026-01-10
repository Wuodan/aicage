from __future__ import annotations

from typing import Any

from aicage.config.errors import ConfigError


def expect_string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{context} must be a non-empty string.")
    return value


def expect_bool(value: Any, context: str) -> bool:
    if not isinstance(value, bool):
        raise ConfigError(f"{context} must be a boolean.")
    return value


def read_str_list(value: Any, context: str) -> list[str]:
    if not isinstance(value, list):
        raise ConfigError(f"{context} must be a list.")
    items: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ConfigError(f"{context} must contain non-empty strings.")
        items.append(item)
    return items


def maybe_str_list(value: Any, context: str) -> list[str] | None:
    if value is None:
        return None
    return read_str_list(value, context)


def expect_keys(
    mapping: dict[str, Any],
    required: set[str],
    optional: set[str],
    context: str,
) -> None:
    missing = sorted(required - set(mapping))
    if missing:
        raise ConfigError(f"{context} missing required keys: {', '.join(missing)}.")
    unknown = sorted(set(mapping) - required - optional)
    if unknown:
        raise ConfigError(f"{context} contains unsupported keys: {', '.join(unknown)}.")
