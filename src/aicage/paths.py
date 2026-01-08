from __future__ import annotations

from pathlib import Path

CONFIG_FILENAME: str = "config.yaml"
PROJECT_CONFIG_FILENAME: str = "project.yaml"
IMAGES_METADATA_FILENAME: str = "images-metadata.yaml"
AGENT_DEFINITION_FILENAME: str = "agent.yaml"

DEFAULT_CUSTOM_AGENTS_DIR: Path = Path("~/.aicage/custom/agents")
CUSTOM_AGENT_DEFINITION_FILES: tuple[str, str] = (
    AGENT_DEFINITION_FILENAME,
    "agent.yml",
)

DEFAULT_CUSTOM_EXTENSIONS_DIR: Path = Path("~/.aicage/custom/extension")
CUSTOM_EXTENSION_DEFINITION_FILES: tuple[str, str] = (
    "extension.yaml",
    "extension.yml",
)
DEFAULT_CUSTOM_EXTENDED_IMAGES_DIR: Path = Path("~/.aicage/custom/image-extended")
EXTENDED_IMAGE_DEFINITION_FILENAME: str = "image-extended.yaml"
