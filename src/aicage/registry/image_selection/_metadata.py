from __future__ import annotations

from aicage.config.images_metadata.models import AgentMetadata, ImagesMetadata
from aicage.registry.errors import RegistryError


def require_agent_metadata(agent: str, images_metadata: ImagesMetadata) -> AgentMetadata:
    agent_metadata = images_metadata.agents.get(agent)
    if not agent_metadata:
        raise RegistryError(f"Agent '{agent}' is missing from images metadata.")
    return agent_metadata


def available_bases(
    agent: str,
    agent_metadata: AgentMetadata,
) -> list[str]:
    if not agent_metadata.valid_bases:
        raise RegistryError(f"Agent '{agent}' does not define any valid bases.")
    return sorted(agent_metadata.valid_bases)


def validate_base(
    agent: str,
    base: str,
    agent_metadata: AgentMetadata,
) -> None:
    if base not in agent_metadata.valid_bases:
        raise RegistryError(f"Base '{base}' is not valid for agent '{agent}'.")
