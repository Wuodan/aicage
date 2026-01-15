from aicage.config.runtime_config import RunConfig
from aicage.paths import CUSTOM_BASES_DIR
from aicage.registry._image_pull import pull_image
from aicage.registry.extension_build.ensure_extended_image import ensure_extended_image
from aicage.registry.local_build.ensure_local_image import ensure_local_image


def ensure_image(run_config: RunConfig) -> None:
    agent_metadata = run_config.context.agents[run_config.agent]
    base_metadata = run_config.context.bases[run_config.selection.base]
    custom_base = base_metadata.local_definition_dir.is_relative_to(CUSTOM_BASES_DIR)
    if not agent_metadata.build_local and not custom_base:
        pull_image(run_config.selection.base_image_ref)
    else:
        ensure_local_image(run_config)
    if run_config.selection.extensions:
        ensure_extended_image(run_config)
