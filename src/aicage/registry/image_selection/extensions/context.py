from dataclasses import dataclass

from aicage.config.context import ConfigContext
from aicage.config.project_config import AgentConfig
from aicage.registry.extensions import ExtensionMetadata
from aicage.registry.images_metadata.models import AgentMetadata


@dataclass(frozen=True)
class ExtensionSelectionContext:
    agent: str
    base: str
    agent_cfg: AgentConfig
    agent_metadata: AgentMetadata
    extensions: dict[str, ExtensionMetadata]
    context: ConfigContext
