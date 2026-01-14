from pathlib import Path
from unittest import mock

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
from aicage.config.project_config import ProjectConfig
from aicage.config.runtime_config import RunConfig
from aicage.registry.image_selection import ImageSelection


def build_run_config(
    build_local: bool = True,
) -> RunConfig:
    return RunConfig(
        project_path=Path("/tmp/project"),
        agent="claude",
        context=ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path="/tmp/project", agents={}),
            images_metadata=build_images_metadata(build_local=build_local),
            extensions={},
        ),
        selection=ImageSelection(
            image_ref="aicage:claude-ubuntu",
            base="ubuntu",
            extensions=[],
            base_image_ref="aicage:claude-ubuntu",
        ),
        project_docker_args="",
        mounts=[],
    )


def build_images_metadata(build_local: bool = True) -> ImagesMetadata:
    return ImagesMetadata.from_mapping(
        {
            _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
            _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
            _BASES_KEY: {
                "ubuntu": {
                    _FROM_IMAGE_KEY: "ubuntu:latest",
                    _BASE_IMAGE_DISTRO_KEY: "Ubuntu",
                    _BASE_IMAGE_DESCRIPTION_KEY: "Default",
                }
            },
            _AGENT_KEY: {
                "claude": {
                    AGENT_PATH_KEY: "~/.claude",
                    AGENT_FULL_NAME_KEY: "Claude Code",
                    AGENT_HOMEPAGE_KEY: "https://example.com",
                    BUILD_LOCAL_KEY: build_local,
                    _VALID_BASES_KEY: {"ubuntu": "ghcr.io/aicage/aicage:claude-ubuntu"},
                }
            },
        }
    )
