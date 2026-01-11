from __future__ import annotations

from aicage.config.runtime_config import RunConfig
from aicage.registry.extension_build.ensure_extended_image import ensure_extended_image
from aicage.registry.image_pull import pull_image
from aicage.registry.local_build.ensure_local_image import ensure_local_image


def ensure_image(run_config: RunConfig) -> None:
    agent_metadata = run_config.context.images_metadata.agents[run_config.agent]
    if agent_metadata.local_definition_dir is None:
        pull_image(run_config.selection.base_image_ref, run_config.context.global_cfg)
    else:
        ensure_local_image(run_config)
    if run_config.selection.extensions:
        ensure_extended_image(run_config)
