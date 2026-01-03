from __future__ import annotations

from pathlib import Path

from aicage.config.resources import find_packaged_path
from aicage.errors import CliError
from aicage.registry.images_metadata.models import AgentMetadata

_AGENT_BUILD_DOCKERFILE = "agent-build/Dockerfile"


def get_agent_build_root() -> Path:
    dockerfile = find_packaged_path(_AGENT_BUILD_DOCKERFILE)
    return dockerfile.parent


def get_agent_definition_dir(agent_name: str, agent_metadata: AgentMetadata) -> Path:
    if agent_metadata.definition_dir is not None:
        return agent_metadata.definition_dir
    if not agent_metadata.build_local:
        raise CliError(f"Agent '{agent_name}' does not have local build definitions.")

    agent_dir = get_agent_build_root() / "agents" / agent_name
    if not agent_dir.is_dir():
        raise CliError(f"Agent '{agent_name}' is missing build definitions at {agent_dir}.")
    return agent_dir
