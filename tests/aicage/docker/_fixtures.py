from pathlib import Path
from unittest import mock

from aicage.config.context import ConfigContext
from aicage.config.images_metadata.models import (
    AgentMetadata,
    BaseMetadata,
    ImagesMetadata,
)
from aicage.config.project_config import ProjectConfig
from aicage.config.runtime_config import RunConfig
from aicage.registry.image_selection.models import ImageSelection


def build_run_config(
    build_local: bool = True,
) -> RunConfig:
    images_metadata = build_images_metadata(build_local=build_local)
    return RunConfig(
        project_path=Path("/tmp/project"),
        agent="claude",
        context=ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path="/tmp/project", agents={}),
            images_metadata=images_metadata,
            agents=images_metadata.agents,
            bases=images_metadata.bases,
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
    bases = {
        "ubuntu": BaseMetadata(
            from_image="ubuntu:latest",
            base_image_distro="Ubuntu",
            base_image_description="Default",
            build_local=False,
            local_definition_dir=Path("/tmp/base"),
        )
    }
    agents = {
        "claude": AgentMetadata(
            agent_path="~/.claude",
            agent_full_name="Claude Code",
            agent_homepage="https://example.com",
            build_local=build_local,
            valid_bases={"ubuntu": "ghcr.io/aicage/aicage:claude-ubuntu"},
            local_definition_dir=Path("/tmp/build/agents/claude"),
        )
    }
    return ImagesMetadata(bases=bases, agents=agents)
