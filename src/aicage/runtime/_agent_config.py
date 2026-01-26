import os
from dataclasses import dataclass
from pathlib import Path

from aicage.config.agent.models import AgentMetadata


@dataclass
class AgentConfig:
    agent_path: list[str]
    agent_config_host: list[Path]


def resolve_agent_config(agent_metadata: AgentMetadata) -> AgentConfig:
    agent_paths = agent_metadata.agent_path
    agent_config_hosts = [_ensure_agent_path(path) for path in agent_paths]
    return AgentConfig(agent_path=agent_paths, agent_config_host=agent_config_hosts)


def _ensure_agent_path(agent_path: str) -> Path:
    expanded = Path(os.path.expanduser(agent_path)).resolve()
    if expanded.exists():
        return expanded
    if _looks_like_file(agent_path):
        expanded.parent.mkdir(parents=True, exist_ok=True)
        expanded.touch()
    else:
        expanded.mkdir(parents=True, exist_ok=True)
    return expanded


def _looks_like_file(agent_path: str) -> bool:
    return bool(Path(agent_path).suffix)
