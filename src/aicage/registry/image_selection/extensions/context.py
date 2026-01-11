from dataclasses import dataclass

from aicage.config.context import ConfigContext
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.images_metadata.models import AgentMetadata
from aicage.config.project_config import AgentConfig


@dataclass(frozen=True)
class ExtensionSelectionContext:
    agent: str
    base: str
    agent_cfg: AgentConfig
    agent_metadata: AgentMetadata
    extensions: dict[str, ExtensionMetadata]
    context: ConfigContext
