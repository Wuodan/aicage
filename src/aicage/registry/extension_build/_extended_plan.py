from __future__ import annotations

from aicage._logging import get_logger
from aicage.config.runtime_config import RunConfig
from aicage.docker.query import local_image_exists
from aicage.registry.layers import base_layer_missing

from ._extended_store import ExtendedBuildRecord


def should_build_extended(
    run_config: RunConfig,
    record: ExtendedBuildRecord | None,
    base_image_ref: str,
    extension_hash: str,
) -> bool:
    needs_rebuild = (
        not local_image_exists(run_config.selection.image_ref)
        or record is None
        or record.image_ref != run_config.selection.image_ref
        or record.extensions != run_config.selection.extensions
        or record.extension_hash != extension_hash
        or record.base_image != base_image_ref
    )
    if needs_rebuild:
        return True
    is_missing = base_layer_missing(base_image_ref, run_config.selection.image_ref)
    if is_missing is None:
        logger = get_logger()
        logger.warning(
            "Skipping base image layer validation for %s; missing local layer data.",
            run_config.selection.image_ref,
        )
        return False
    return is_missing
