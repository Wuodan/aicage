from dataclasses import dataclass

from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.images_metadata.models import AgentMetadata, BaseMetadata, ImagesMetadata
from aicage.constants import IMAGE_REGISTRY, IMAGE_REPOSITORY

from .config_store import SettingsStore
from .project_config import ProjectConfig


@dataclass
class ConfigContext:
    store: SettingsStore
    project_cfg: ProjectConfig
    images_metadata: ImagesMetadata
    agents: dict[str, AgentMetadata]
    bases: dict[str, BaseMetadata]
    extensions: dict[str, ExtensionMetadata]

    @staticmethod
    def image_repository_ref() -> str:
        return f"{IMAGE_REGISTRY}/{IMAGE_REPOSITORY}"
