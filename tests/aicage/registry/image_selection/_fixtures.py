from pathlib import Path

from aicage.config import GlobalConfig, ProjectConfig
from aicage.config.config_store import SettingsStore
from aicage.config.context import ConfigContext
from aicage.config.images_metadata.models import (
    _AGENT_KEY,
    _AICAGE_IMAGE_BASE_KEY,
    _AICAGE_IMAGE_KEY,
    _BASE_IMAGE_DESCRIPTION_KEY,
    _BASE_IMAGE_DISTRO_KEY,
    _BASES_KEY,
    _OS_INSTALLER_KEY,
    _ROOT_IMAGE_KEY,
    _TEST_SUITE_KEY,
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
        global_cfg=global_config(),
        images_metadata=metadata_with_bases(bases),
        extensions={},
    )


def global_config() -> GlobalConfig:
    return GlobalConfig(
        image_registry="ghcr.io",
        image_registry_api_url="https://ghcr.io/v2",
        image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
        image_repository="aicage/aicage",
        image_base_repository="aicage/aicage-image-base",
        default_image_base="ubuntu",
        version_check_image="ghcr.io/aicage/aicage-image-util:agent-version",
        local_image_repository="aicage",
        agents={},
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
                    _ROOT_IMAGE_KEY: "ubuntu:latest",
                    _BASE_IMAGE_DISTRO_KEY: "Ubuntu",
                    _BASE_IMAGE_DESCRIPTION_KEY: "Default",
                    _OS_INSTALLER_KEY: "distro/debian/install.sh",
                    _TEST_SUITE_KEY: "default",
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
