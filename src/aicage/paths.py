from __future__ import annotations

from pathlib import Path

CONFIG_FILENAME: str = "config.yaml"
IMAGES_METADATA_FILENAME: str = "images-metadata.yaml"
_AGENT_DEFINITION_FILENAME: str = "agent.yaml"

DEFAULT_CUSTOM_AGENTS_DIR: Path = Path("~/.aicage/custom/agents")
CUSTOM_AGENT_DEFINITION_FILES: tuple[str, str] = (
    _AGENT_DEFINITION_FILENAME,
    "agent.yml",
)

DEFAULT_CUSTOM_EXTENSIONS_DIR: Path = Path("~/.aicage/custom/extensions")
CUSTOM_EXTENSION_DEFINITION_FILES: tuple[str, str] = (
    "extension.yaml",
    "extension.yml",
)
DEFAULT_CUSTOM_EXTENDED_IMAGES_DIR: Path = Path("~/.aicage/custom/image-extended")
EXTENDED_IMAGE_DEFINITION_FILENAME: str = "image-extended.yaml"

DEFAULT_CUSTOM_BASES_DIR: Path = Path("~/.aicage/custom/base-images")
CUSTOM_BASE_DEFINITION_FILES: tuple[str, str] = (
    "base.yaml",
    "base.yml",
)

DEFAULT_VERSION_CHECK_STATE_DIR: Path = Path("~/.aicage/state/version-check")
DEFAULT_LOCAL_BUILD_STATE_DIR: Path = Path("~/.aicage/state/local-build")
DEFAULT_LOCAL_EXTENDED_STATE_DIR: Path = Path("~/.aicage/state/local-extended")
