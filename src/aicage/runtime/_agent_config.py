import os
from dataclasses import dataclass
from pathlib import Path

from aicage.config.images_metadata.models import AgentMetadata, ImagesMetadata
from aicage.runtime.errors import RuntimeExecutionError


@dataclass
class AgentConfig:
    agent_path: str
    agent_config_host: Path


def resolve_agent_config(agent: str, images_metadata: ImagesMetadata) -> AgentConfig:
    agent_path = _read_agent_path(agent, images_metadata)
    agent_config_host = Path(os.path.expanduser(agent_path)).resolve()
    agent_config_host.mkdir(parents=True, exist_ok=True)
    return AgentConfig(agent_path=agent_path, agent_config_host=agent_config_host)


def _read_agent_path(agent: str, images_metadata: ImagesMetadata) -> str:
    agent_metadata = _require_agent_metadata(agent, images_metadata)
    return agent_metadata.agent_path


def _require_agent_metadata(agent: str, images_metadata: ImagesMetadata) -> AgentMetadata:
    agent_metadata = images_metadata.agents.get(agent)
    if not agent_metadata:
        raise RuntimeExecutionError(f"Agent '{agent}' is missing from images metadata.")
    return agent_metadata
