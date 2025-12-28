from dataclasses import dataclass
from pathlib import Path

from aicage.registry.images_metadata.loader import load_images_metadata
from aicage.registry.images_metadata.models import ImagesMetadata

from .config_store import SettingsStore
from .global_config import GlobalConfig
from .project_config import ProjectConfig


@dataclass
class ConfigContext:
    store: SettingsStore
    project_cfg: ProjectConfig
    global_cfg: GlobalConfig
    images_metadata: ImagesMetadata

    def image_repository_ref(self) -> str:
        return f"{self.global_cfg.image_registry}/{self.global_cfg.image_repository}"


def build_config_context() -> ConfigContext:
    store = SettingsStore()
    project_path = Path.cwd().resolve()
    global_cfg = store.load_global()
    images_metadata = load_images_metadata()
    project_cfg = store.load_project(project_path)
    return ConfigContext(
        store=store,
        project_cfg=project_cfg,
        global_cfg=global_cfg,
        images_metadata=images_metadata,
    )


__all__ = ["ConfigContext", "build_config_context"]
