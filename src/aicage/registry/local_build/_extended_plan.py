from __future__ import annotations

from aicage._logging import get_logger
from aicage.config.runtime_config import RunConfig

from ._extended_store import ExtendedBuildRecord
from ._layers import get_local_rootfs_layers
from ._runner import local_image_exists


def should_build_extended(
    run_config: RunConfig,
    record: ExtendedBuildRecord | None,
    base_image_ref: str,
    extension_hash: str,
) -> bool:
    needs_rebuild = (
        not local_image_exists(run_config.image_ref)
        or record is None
        or record.image_ref != run_config.image_ref
        or record.extensions != run_config.extensions
        or record.extension_hash != extension_hash
        or record.base_image != base_image_ref
    )
    if needs_rebuild:
        return True
    base_layer_missing = _base_layer_missing(base_image_ref, run_config.image_ref)
    if base_layer_missing is None:
        logger = get_logger()
        logger.warning(
            "Skipping base image layer validation for %s; missing local layer data.",
            run_config.image_ref,
        )
        return False
    return base_layer_missing


def _base_layer_missing(base_image_ref: str, final_image_ref: str) -> bool | None:
    base_layers = get_local_rootfs_layers(base_image_ref)
    if base_layers is None:
        return None
    final_layers = get_local_rootfs_layers(final_image_ref)
    if final_layers is None:
        return None
    return base_layers[-1] not in final_layers
