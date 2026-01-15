from pathlib import Path

from aicage.config.agent._metadata import build_agent_metadata
from aicage.config.agent._validation import ensure_required_files
from aicage.config.agent.models import AgentMetadata
from aicage.config.base.models import BaseMetadata
from aicage.config.errors import ConfigError
from aicage.config.yaml_loader import load_yaml
from aicage.paths import CUSTOM_AGENT_DEFINITION_FILES, CUSTOM_AGENTS_DIR


def load_custom_agents(
    bases: dict[str, BaseMetadata],
) -> dict[str, AgentMetadata]:
    agents_dir = CUSTOM_AGENTS_DIR
    if not agents_dir.is_dir():
        return {}

    custom_agents: dict[str, AgentMetadata] = {}
    for entry in sorted(agents_dir.iterdir()):
        if not entry.is_dir():
            continue
        agent_name = entry.name
        agent_path = _find_agent_definition(entry)
        agent_mapping = load_yaml(agent_path)
        ensure_required_files(agent_name, entry)
        custom_agents[agent_name] = build_agent_metadata(
            agent_name=agent_name,
            agent_mapping=agent_mapping,
            bases=bases,
            definition_dir=entry,
        )
    return custom_agents


def _find_agent_definition(agent_dir: Path) -> Path:
    for filename in CUSTOM_AGENT_DEFINITION_FILES:
        candidate = agent_dir / filename
        if candidate.is_file():
            return candidate
    expected = ", ".join(CUSTOM_AGENT_DEFINITION_FILES)
    raise ConfigError(f"Custom agent '{agent_dir.name}' is missing {expected}.")
