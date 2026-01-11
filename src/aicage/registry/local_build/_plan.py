from __future__ import annotations

from aicage._logging import get_logger
from aicage.config.runtime_config import RunConfig
from aicage.docker.query import local_image_exists
from aicage.registry.layers import base_layer_missing

from ._refs import get_base_image_ref
from ._store import BuildRecord


def should_build(
    run_config: RunConfig,
    record: BuildRecord | None,
    agent_version: str,
) -> bool:
    base_image_ref = get_base_image_ref(run_config)
    image_ref = run_config.selection.base_image_ref
    if not local_image_exists(image_ref):
        return True
    if record is None:
        return True
    if record.agent_version != agent_version:
        return True
    is_missing = base_layer_missing(base_image_ref, image_ref)
    if is_missing is None:
        logger = get_logger()
        logger.warning(
            "Skipping base image layer validation for %s; missing local layer data.",
            image_ref,
        )
        return False
    if is_missing:
        return True
    return False

