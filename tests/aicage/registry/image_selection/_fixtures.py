from pathlib import Path

from aicage.config import ProjectConfig
from aicage.config.config_store import SettingsStore
from aicage.config.context import ConfigContext
from aicage.config.images_metadata.models import (
    _AGENT_KEY,
    _AICAGE_IMAGE_BASE_KEY,
    _AICAGE_IMAGE_KEY,
    _BASE_IMAGE_DESCRIPTION_KEY,
    _BASE_IMAGE_DISTRO_KEY,
    _BASES_KEY,
    _FROM_IMAGE_KEY,
    _VALID_BASES_KEY,
    _VERSION_KEY,
    AGENT_FULL_NAME_KEY,
    AGENT_HOMEPAGE_KEY,
    AGENT_PATH_KEY,
    BUILD_LOCAL_KEY,
    ImagesMetadata,
)
from aicage.config.project_config import AgentConfig


def build_context(
    store: SettingsStore,
    project_path: Path,
    bases: list[str],
    agents: dict[str, AgentConfig] | None = None,
) -> ConfigContext:
    return ConfigContext(
        store=store,
        project_cfg=ProjectConfig(path=str(project_path), agents=agents or {}),
        images_metadata=metadata_with_bases(bases),
        extensions={},
    )


def metadata_with_bases(
    bases: list[str],
    agent_name: str = "codex",
    build_local: bool = False,
) -> ImagesMetadata:
    return ImagesMetadata.from_mapping(
        {
            _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
            _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
            _BASES_KEY: {
                name: {
                    _FROM_IMAGE_KEY: "ubuntu:latest",
                    _BASE_IMAGE_DISTRO_KEY: "Ubuntu",
                    _BASE_IMAGE_DESCRIPTION_KEY: "Default",
                }
                for name in bases
            },
            _AGENT_KEY: {
                agent_name: {
                    AGENT_PATH_KEY: "~/.codex",
                    AGENT_FULL_NAME_KEY: "Codex CLI",
                    AGENT_HOMEPAGE_KEY: "https://example.com",
                    BUILD_LOCAL_KEY: build_local,
                    _VALID_BASES_KEY: {
                        name: f"ghcr.io/aicage/aicage:{agent_name}-{name}"
                        for name in bases
                    },
                }
            },
        }
    )
