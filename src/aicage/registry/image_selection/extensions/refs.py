from aicage.config.context import ConfigContext
from aicage.config.custom_base.loader import load_custom_base
from aicage.config.image_refs import local_image_ref
from aicage.config.images_metadata.models import AgentMetadata


def base_image_ref(
    agent_metadata: AgentMetadata,
    agent: str,
    base: str,
    context: ConfigContext,
) -> str:
    if agent_metadata.build_local or load_custom_base(base) is not None:
        return local_image_ref(context.global_cfg.local_image_repository, agent, base)
    return agent_metadata.valid_bases[base]
