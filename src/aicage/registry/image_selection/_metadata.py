from aicage.config.agent.models import AgentMetadata
from aicage.config.base.filter import filter_bases
from aicage.config.context import ConfigContext
from aicage.registry._errors import RegistryError


def require_agent_metadata(agent: str, context: ConfigContext) -> AgentMetadata:
    agent_metadata = context.agents.get(agent)
    if not agent_metadata:
        raise RegistryError(f"Agent '{agent}' is missing from config context.")
    return agent_metadata


def available_bases(
    agent: str,
    context: ConfigContext,
) -> list[str]:
    agent_metadata = require_agent_metadata(agent, context)
    filtered = filter_bases(context, agent_metadata)
    if not filtered:
        raise RegistryError(f"Agent '{agent}' does not define any valid bases.")
    return sorted(filtered)


def validate_base(
    agent: str,
    base: str,
    context: ConfigContext,
) -> None:
    agent_metadata = require_agent_metadata(agent, context)
    if base not in filter_bases(context, agent_metadata):
        raise RegistryError(f"Base '{base}' is not valid for agent '{agent}'.")
