from pathlib import Path

from aicage.config.agent._custom_loader import load_custom_agents
from aicage.config.agent._metadata import build_agent_metadata
from aicage.config.agent._validation import ensure_required_files
from aicage.config.agent.models import AgentMetadata
from aicage.config.base.models import BaseMetadata
from aicage.config.errors import ConfigError
from aicage.config.resources import find_packaged_path
from aicage.config.yaml_loader import load_yaml

_AGENT_DEFINITION_FILES: tuple[str, str] = ("agent.yaml", "agent.yml")


def load_agents(bases: dict[str, BaseMetadata]) -> dict[str, AgentMetadata]:
    builtin_agents = _load_builtin_agents(bases)
    custom_agents = load_custom_agents(bases)
    merged_agents = dict(builtin_agents)
    merged_agents.update(custom_agents)
    return merged_agents


def _load_builtin_agents(bases: dict[str, BaseMetadata]) -> dict[str, AgentMetadata]:
    agents_dir = _builtin_agents_dir()
    if not agents_dir.is_dir():
        raise ConfigError(f"Built-in agent directory '{agents_dir}' is missing.")

    agents: dict[str, AgentMetadata] = {}
    for entry in sorted(agents_dir.iterdir()):
        if not entry.is_dir():
            continue
        agent_name = entry.name
        agent_path = _find_agent_definition(entry)
        agent_mapping = load_yaml(agent_path)
        ensure_required_files(agent_name, entry)
        agents[agent_name] = build_agent_metadata(
            agent_name=agent_name,
            agent_mapping=agent_mapping,
            bases=bases,
            definition_dir=entry,
        )
    return agents


def _builtin_agents_dir() -> Path:
    dockerfile = find_packaged_path("agent-build/Dockerfile")
    return dockerfile.parent / "agents"


def _find_agent_definition(agent_dir: Path) -> Path:
    for filename in _AGENT_DEFINITION_FILES:
        candidate = agent_dir / filename
        if candidate.is_file():
            return candidate
    expected = ", ".join(_AGENT_DEFINITION_FILES)
    raise ConfigError(f"Agent '{agent_dir.name}' is missing {expected}.")
