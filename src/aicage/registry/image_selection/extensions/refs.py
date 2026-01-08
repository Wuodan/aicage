from aicage.config.context import ConfigContext
from aicage.registry._image_refs import local_image_ref
from aicage.registry.images_metadata.models import AgentMetadata


def base_image_ref(
    agent_metadata: AgentMetadata,
    agent: str,
    base: str,
    context: ConfigContext,
) -> str:
    if agent_metadata.local_definition_dir is not None:
        return local_image_ref(context.global_cfg.local_image_repository, agent, base)
    return agent_metadata.valid_bases[base]
