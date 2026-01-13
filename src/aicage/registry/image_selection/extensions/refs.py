from aicage.config.context import ConfigContext
from aicage.config.image_refs import local_image_ref
from aicage.config.images_metadata.models import AgentMetadata
from aicage.constants import LOCAL_IMAGE_REPOSITORY


def base_image_ref(
    agent_metadata: AgentMetadata,
    agent: str,
    base: str,
    context: ConfigContext,
) -> str:
    if agent_metadata.build_local or context.custom_bases.get(base) is not None:
        return local_image_ref(LOCAL_IMAGE_REPOSITORY, agent, base)
    return agent_metadata.valid_bases[base]
