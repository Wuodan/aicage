from __future__ import annotations

from aicage.config.runtime_config import RunConfig
from aicage.registry.image_pull import pull_image
from aicage.registry.local_build.ensure_extended_image import ensure_extended_image
from aicage.registry.local_build.ensure_local_image import ensure_local_image


def ensure_image(run_config: RunConfig) -> None:
    agent_metadata = run_config.images_metadata.agents[run_config.agent]
    if agent_metadata.local_definition_dir is None:
        pull_image(run_config.base_image_ref, run_config.global_cfg)
    else:
        ensure_local_image(run_config, run_config.base_image_ref)
    if run_config.extensions:
        ensure_extended_image(run_config)
