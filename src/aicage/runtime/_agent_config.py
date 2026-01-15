import os
from dataclasses import dataclass
from pathlib import Path

from aicage.config.agent.models import AgentMetadata


@dataclass
class AgentConfig:
    agent_path: str
    agent_config_host: Path


def resolve_agent_config(agent_metadata: AgentMetadata) -> AgentConfig:
    agent_path = agent_metadata.agent_path
    agent_config_host = Path(os.path.expanduser(agent_path)).resolve()
    agent_config_host.mkdir(parents=True, exist_ok=True)
    return AgentConfig(agent_path=agent_path, agent_config_host=agent_config_host)
