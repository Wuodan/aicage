from __future__ import annotations

from aicage.config.errors import ConfigError
from aicage.config.resources import find_packaged_path
from aicage.paths import IMAGES_METADATA_FILENAME

from ._agent_discovery import discover_agents
from ._base_discovery import discover_bases
from .models import BaseMetadata, ImagesMetadata


def load_images_metadata(custom_bases: dict[str, BaseMetadata]) -> ImagesMetadata:
    path = find_packaged_path(IMAGES_METADATA_FILENAME)
    try:
        payload = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"Failed to read images metadata from {path}: {exc}") from exc
    metadata = ImagesMetadata.from_yaml(payload)
    metadata = discover_bases(metadata, custom_bases)
    return discover_agents(metadata)
