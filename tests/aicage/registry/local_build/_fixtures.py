from pathlib import Path
from unittest import mock

from aicage.config.agent.models import AgentMetadata
from aicage.config.base.models import BaseMetadata
from aicage.config.context import ConfigContext
from aicage.config.project_config import ProjectConfig
from aicage.config.runtime_config import RunConfig
from aicage.registry.image_selection.models import ImageSelection


def build_run_config(
    build_local: bool = True,
) -> RunConfig:
    bases, agents = build_agents_and_bases(build_local=build_local)
    return RunConfig(
        project_path=Path("/tmp/project"),
        agent="claude",
        context=ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path="/tmp/project", agents={}),
            agents=agents,
            bases=bases,
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
        env=[],
    )


def build_agents_and_bases(
    build_local: bool = True,
) -> tuple[dict[str, BaseMetadata], dict[str, AgentMetadata]]:
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
            local_definition_dir=Path("/tmp/agent"),
        )
    }
    return bases, agents
