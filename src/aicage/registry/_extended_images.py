from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from aicage._logging import get_logger
from aicage.errors import CliError
from aicage.paths import DEFAULT_CUSTOM_EXTENDED_IMAGES_DIR, EXTENDED_IMAGE_DEFINITION_FILENAME

_AGENT_KEY: str = "agent"
_BASE_KEY: str = "base"
_EXTENSIONS_KEY: str = "extensions"
_IMAGE_REF_KEY: str = "image_ref"


@dataclass(frozen=True)
class ExtendedImageConfig:
    name: str
    agent: str
    base: str
    extensions: list[str]
    image_ref: str
    path: Path


def load_extended_images(available_extensions: set[str]) -> dict[str, ExtendedImageConfig]:
    images_dir = DEFAULT_CUSTOM_EXTENDED_IMAGES_DIR.expanduser()
    if not images_dir.is_dir():
        return {}
    configs: dict[str, ExtendedImageConfig] = {}
    logger = get_logger()
    for entry in sorted(images_dir.iterdir()):
        if not entry.is_dir():
            continue
        config_path = entry / EXTENDED_IMAGE_DEFINITION_FILENAME
        if not config_path.is_file():
            raise CliError(
                f"Extended image '{entry.name}' is missing {EXTENDED_IMAGE_DEFINITION_FILENAME}."
            )
        mapping = _load_yaml(config_path)
        _expect_keys(
            mapping,
            required={_AGENT_KEY, _BASE_KEY, _EXTENSIONS_KEY, _IMAGE_REF_KEY},
            optional=set(),
            context=f"extended image config at {config_path}",
        )
        extensions = _read_str_list(mapping.get(_EXTENSIONS_KEY), _EXTENSIONS_KEY)
        missing = [ext for ext in extensions if ext not in available_extensions]
        if missing:
            logger.warning(
                "Skipping extended image %s; missing extensions: %s",
                entry.name,
                ", ".join(sorted(missing)),
            )
            continue
        configs[entry.name] = ExtendedImageConfig(
            name=entry.name,
            agent=_expect_string(mapping.get(_AGENT_KEY), _AGENT_KEY),
            base=_expect_string(mapping.get(_BASE_KEY), _BASE_KEY),
            extensions=extensions,
            image_ref=_expect_string(mapping.get(_IMAGE_REF_KEY), _IMAGE_REF_KEY),
            path=config_path,
        )
    return configs


def write_extended_image_config(config: ExtendedImageConfig) -> None:
    config.path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        _AGENT_KEY: config.agent,
        _BASE_KEY: config.base,
        _EXTENSIONS_KEY: list(config.extensions),
        _IMAGE_REF_KEY: config.image_ref,
    }
    config.path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")


def extended_image_config_path(name: str) -> Path:
    return (
        DEFAULT_CUSTOM_EXTENDED_IMAGES_DIR.expanduser()
        / name
        / EXTENDED_IMAGE_DEFINITION_FILENAME
    )


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        payload = path.read_text(encoding="utf-8")
        data = yaml.safe_load(payload) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise CliError(f"Failed to read extended image config from {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise CliError(f"Extended image config at {path} must be a mapping.")
    return data


def _expect_string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CliError(f"{context} must be a non-empty string.")
    return value


def _read_str_list(value: Any, context: str) -> list[str]:
    if not isinstance(value, list):
        raise CliError(f"{context} must be a list.")
    items: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise CliError(f"{context} must contain non-empty strings.")
        items.append(item)
    return items


def _expect_keys(
    mapping: dict[str, Any],
    required: set[str],
    optional: set[str],
    context: str,
) -> None:
    missing = sorted(required - set(mapping))
    if missing:
        raise CliError(f"{context} missing required keys: {', '.join(missing)}.")
    unknown = sorted(set(mapping) - required - optional)
    if unknown:
        raise CliError(f"{context} contains unsupported keys: {', '.join(unknown)}.")
