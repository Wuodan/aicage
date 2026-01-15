from __future__ import annotations

from .models import AgentMetadata, BaseMetadata, ImagesMetadata


def load_images_metadata(
    bases: dict[str, BaseMetadata],
    agents: dict[str, AgentMetadata],
) -> ImagesMetadata:
    return ImagesMetadata(bases=bases, agents=agents)
