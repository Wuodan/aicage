import os
from dataclasses import dataclass
from pathlib import Path

from aicage.config.agent.models import AgentMetadata
from aicage.runtime._errors import RuntimeExecutionError


@dataclass
class AgentConfig:
    agent_path: str
    agent_config_host: Path


def resolve_agent_config(agent: str, agents: dict[str, AgentMetadata]) -> AgentConfig:
    agent_path = _read_agent_path(agent, agents)
    agent_config_host = Path(os.path.expanduser(agent_path)).resolve()
    agent_config_host.mkdir(parents=True, exist_ok=True)
    return AgentConfig(agent_path=agent_path, agent_config_host=agent_config_host)


def _read_agent_path(agent: str, agents: dict[str, AgentMetadata]) -> str:
    agent_metadata = _require_agent_metadata(agent, agents)
    return agent_metadata.agent_path


def _require_agent_metadata(agent: str, agents: dict[str, AgentMetadata]) -> AgentMetadata:
    agent_metadata = agents.get(agent)
    if not agent_metadata:
        raise RuntimeExecutionError(f"Agent '{agent}' is missing from config context.")
    return agent_metadata
