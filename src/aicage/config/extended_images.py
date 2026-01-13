from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from aicage._logging import get_logger
from aicage.config._yaml import expect_keys, expect_string, read_str_list
from aicage.config.errors import ConfigError
from aicage.config.yaml_loader import load_yaml
from aicage.paths import EXTENDED_IMAGE_DEFINITION_FILENAME, IMAGE_EXTENDED_STATE_DIR

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
    images_dir = IMAGE_EXTENDED_STATE_DIR
    if not images_dir.is_dir():
        return {}
    configs: dict[str, ExtendedImageConfig] = {}
    logger = get_logger()
    for entry in sorted(images_dir.iterdir()):
        if not entry.is_dir():
            continue
        config_path = entry / EXTENDED_IMAGE_DEFINITION_FILENAME
        if not config_path.is_file():
            raise ConfigError(
                f"Extended image '{entry.name}' is missing {EXTENDED_IMAGE_DEFINITION_FILENAME}."
            )
        mapping = load_yaml(config_path)
        expect_keys(
            mapping,
            required={_AGENT_KEY, _BASE_KEY, _EXTENSIONS_KEY, _IMAGE_REF_KEY},
            optional=set(),
            context=f"extended image config at {config_path}",
        )
        extensions = read_str_list(mapping.get(_EXTENSIONS_KEY), _EXTENSIONS_KEY)
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
            agent=expect_string(mapping.get(_AGENT_KEY), _AGENT_KEY),
            base=expect_string(mapping.get(_BASE_KEY), _BASE_KEY),
            extensions=extensions,
            image_ref=expect_string(mapping.get(_IMAGE_REF_KEY), _IMAGE_REF_KEY),
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
        IMAGE_EXTENDED_STATE_DIR
        / name
        / EXTENDED_IMAGE_DEFINITION_FILENAME
    )
