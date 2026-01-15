from pathlib import Path

from aicage.config._yaml import expect_bool, expect_string
from aicage.config.base._custom_loader import load_custom_bases
from aicage.config.base._validation import validate_base_mapping
from aicage.config.base.models import BUILD_LOCAL_KEY, BaseMetadata
from aicage.config.errors import ConfigError
from aicage.config.resources import find_packaged_path
from aicage.config.yaml_loader import load_yaml

_BASES_DIR_NAME: str = "base-build/bases"
_BASE_DEFINITION_FILES: tuple[str, str] = ("base.yaml", "base.yml")
_FROM_IMAGE_KEY: str = "from_image"
_BASE_IMAGE_DISTRO_KEY: str = "base_image_distro"
_BASE_IMAGE_DESCRIPTION_KEY: str = "base_image_description"


def load_bases() -> dict[str, BaseMetadata]:
    builtin_bases = _load_builtin_bases()
    custom_bases = load_custom_bases()
    merged_bases = dict(builtin_bases)
    merged_bases.update(custom_bases)
    return merged_bases


def _load_builtin_bases() -> dict[str, BaseMetadata]:
    bases_dir = _builtin_bases_dir()
    if not bases_dir.is_dir():
        raise ConfigError(f"Built-in base directory '{bases_dir}' is missing.")

    bases: dict[str, BaseMetadata] = {}
    for entry in sorted(bases_dir.iterdir()):
        if not entry.is_dir():
            continue
        base_name = entry.name
        definition_path = _find_base_definition(entry)
        mapping = validate_base_mapping(load_yaml(definition_path))
        bases[base_name] = BaseMetadata(
            from_image=expect_string(mapping.get(_FROM_IMAGE_KEY), _FROM_IMAGE_KEY),
            base_image_distro=expect_string(mapping.get(_BASE_IMAGE_DISTRO_KEY), _BASE_IMAGE_DISTRO_KEY),
            base_image_description=expect_string(
                mapping.get(_BASE_IMAGE_DESCRIPTION_KEY),
                _BASE_IMAGE_DESCRIPTION_KEY,
            ),
            build_local=expect_bool(mapping.get(BUILD_LOCAL_KEY), BUILD_LOCAL_KEY),
            local_definition_dir=entry,
        )
    return bases


def _builtin_bases_dir() -> Path:
    dockerfile = find_packaged_path("agent-build/Dockerfile")
    return dockerfile.parent.parent / _BASES_DIR_NAME


def _find_base_definition(base_dir: Path) -> Path:
    for filename in _BASE_DEFINITION_FILES:
        candidate = base_dir / filename
        if candidate.is_file():
            return candidate
    expected = ", ".join(_BASE_DEFINITION_FILES)
    raise ConfigError(f"Base '{base_dir.name}' is missing {expected}.")
