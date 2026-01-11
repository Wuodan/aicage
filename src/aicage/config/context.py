from dataclasses import dataclass

from aicage.config.extensions import ExtensionMetadata
from aicage.config.images_metadata.models import ImagesMetadata

from .config_store import SettingsStore
from .global_config import GlobalConfig
from .project_config import ProjectConfig


@dataclass
class ConfigContext:
    store: SettingsStore
    project_cfg: ProjectConfig
    global_cfg: GlobalConfig
    images_metadata: ImagesMetadata
    extensions: dict[str, ExtensionMetadata]

    def image_repository_ref(self) -> str:
        return f"{self.global_cfg.image_registry}/{self.global_cfg.image_repository}"
