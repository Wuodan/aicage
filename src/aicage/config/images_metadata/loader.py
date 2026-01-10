from __future__ import annotations

from aicage.config.errors import ConfigError
from aicage.config.resources import find_packaged_path
from aicage.paths import IMAGES_METADATA_FILENAME

from ._agent_discovery import discover_agents
from .models import ImagesMetadata


def load_images_metadata(local_image_repository: str) -> ImagesMetadata:
    path = find_packaged_path(IMAGES_METADATA_FILENAME)
    try:
        payload = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"Failed to read images metadata from {path}: {exc}") from exc
    metadata = ImagesMetadata.from_yaml(payload)
    return discover_agents(metadata, local_image_repository)
