from __future__ import annotations

from os.path import expanduser
from pathlib import Path

IMAGES_METADATA_FILENAME: str = "images-metadata.yaml"
_AGENT_DEFINITION_FILENAME: str = "agent.yaml"
EXTENDED_IMAGE_DEFINITION_FILENAME: str = "image-extended.yaml"

_CONFIG_BASE_DIR: Path = Path(expanduser("~/.aicage"))
PROJECTS_DIR: Path = _CONFIG_BASE_DIR / "projects"

BASE_IMAGE_BUILD_STATE_DIR: Path = _CONFIG_BASE_DIR / "state/base-image/build"
IMAGE_BUILD_STATE_DIR: Path = _CONFIG_BASE_DIR / "state/image/build"
AGENT_VERSION_CHECK_STATE_DIR: Path = _CONFIG_BASE_DIR / "state/agent/version-check/state"
IMAGE_EXTENDED_STATE_DIR: Path = _CONFIG_BASE_DIR / "state/image-extended"
IMAGE_EXTENDED_BUILD_STATE_DIR: Path = IMAGE_EXTENDED_STATE_DIR / "build"

_LOG_DIR: Path = _CONFIG_BASE_DIR / "logs"
GLOBAL_LOG_PATH: Path = _LOG_DIR / "aicage.log"
IMAGE_PULL_LOG_DIR: Path = _LOG_DIR / "image/pull"
BASE_IMAGE_BUILD_LOG_DIR: Path = _LOG_DIR / "base-image/build"
IMAGE_BUILD_LOG_DIR: Path = _LOG_DIR / "image/build"
IMAGE_EXTENDED_BUILD_LOG_DIR: Path = _LOG_DIR / "image-extended/build"

# Only user-generated custom files outside ~/.aicage.
_CUSTOM_ROOT_DIR: Path = Path(expanduser("~/.aicage-custom"))

CUSTOM_BASES_DIR: Path = _CUSTOM_ROOT_DIR / "base-images"
CUSTOM_BASE_DEFINITION_FILES: tuple[str, str] = (
    "base.yaml",
    "base.yml",
)

CUSTOM_AGENTS_DIR: Path = _CUSTOM_ROOT_DIR / "agents"
CUSTOM_AGENT_DEFINITION_FILES: tuple[str, str] = (
    _AGENT_DEFINITION_FILENAME,
    "agent.yml",
)

CUSTOM_EXTENSIONS_DIR: Path = _CUSTOM_ROOT_DIR / "extensions"
CUSTOM_EXTENSION_DEFINITION_FILES: tuple[str, str] = (
    "extension.yaml",
    "extension.yml",
)
