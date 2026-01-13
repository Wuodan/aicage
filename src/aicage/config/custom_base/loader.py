from __future__ import annotations

from pathlib import Path

from aicage.config._yaml import expect_string
from aicage.config.errors import ConfigError
from aicage.config.yaml_loader import load_yaml
from aicage.paths import CUSTOM_BASE_DEFINITION_FILES, CUSTOM_BASES_DIR

from ..images_metadata.models import BaseMetadata
from ._validation import validate_base_mapping

_FROM_IMAGE_KEY: str = "from_image"
_BASE_IMAGE_DISTRO_KEY: str = "base_image_distro"
_BASE_IMAGE_DESCRIPTION_KEY: str = "base_image_description"

_DOCKERFILE_NAME: str = "Dockerfile"


def load_custom_bases() -> dict[str, BaseMetadata]:
    bases_dir = CUSTOM_BASES_DIR
    if not bases_dir.is_dir():
        return {}

    custom_bases: dict[str, BaseMetadata] = {}
    for entry in sorted(bases_dir.iterdir()):
        if not entry.is_dir():
            continue
        base_name = entry.name
        custom_bases[base_name] = _load_custom_base(base_name)
    return custom_bases


def _load_custom_base(base_name: str) -> BaseMetadata:
    base_dir = CUSTOM_BASES_DIR / base_name
    definition_path = _find_base_definition(base_dir)
    _ensure_required_files(base_name, base_dir)
    mapping = validate_base_mapping(load_yaml(definition_path))
    return BaseMetadata(
        from_image=expect_string(mapping.get(_FROM_IMAGE_KEY), _FROM_IMAGE_KEY),
        base_image_distro=expect_string(mapping.get(_BASE_IMAGE_DISTRO_KEY), _BASE_IMAGE_DISTRO_KEY),
        base_image_description=expect_string(
            mapping.get(_BASE_IMAGE_DESCRIPTION_KEY),
            _BASE_IMAGE_DESCRIPTION_KEY,
        ),
        os_installer="",
        test_suite="",
    )


def _find_base_definition(base_dir: Path) -> Path:
    for filename in CUSTOM_BASE_DEFINITION_FILES:
        candidate = base_dir / filename
        if candidate.is_file():
            return candidate
    expected = ", ".join(CUSTOM_BASE_DEFINITION_FILES)
    raise ConfigError(f"Custom base '{base_dir.name}' is missing {expected}.")


def _ensure_required_files(base_name: str, base_dir: Path) -> None:
    dockerfile = base_dir / _DOCKERFILE_NAME
    if not dockerfile.is_file():
        raise ConfigError(f"Custom base '{base_name}' is missing {_DOCKERFILE_NAME}.")
