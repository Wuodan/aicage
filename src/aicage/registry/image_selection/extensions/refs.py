from aicage.config.context import ConfigContext
from aicage.config.image_refs import local_image_ref
from aicage.config.images_metadata.models import AgentMetadata
from aicage.constants import LOCAL_IMAGE_REPOSITORY
from aicage.paths import CUSTOM_BASES_DIR


def base_image_ref(
    agent_metadata: AgentMetadata,
    agent: str,
    base: str,
    context: ConfigContext,
) -> str:
    base_metadata = context.bases[base]
    if agent_metadata.build_local or base_metadata.local_definition_dir.is_relative_to(CUSTOM_BASES_DIR):
        return local_image_ref(LOCAL_IMAGE_REPOSITORY, agent, base)
    return agent_metadata.valid_bases[base]
