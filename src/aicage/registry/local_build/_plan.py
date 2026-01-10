from __future__ import annotations

from datetime import datetime, timezone

from aicage._logging import get_logger
from aicage.config.runtime_config import RunConfig
from aicage.docker.query import get_local_rootfs_layers, local_image_exists

from ._store import BuildRecord


def should_build(
    run_config: RunConfig,
    record: BuildRecord | None,
    base_image_ref: str,
) -> bool:
    if not local_image_exists(run_config.image_ref):
        return True
    if record is None:
        return True
    if record.agent_version != run_config.agent_version:
        return True
    base_layer_missing = _base_layer_missing(base_image_ref, run_config.image_ref)
    if base_layer_missing is None:
        logger = get_logger()
        logger.warning(
            "Skipping base image layer validation for %s; missing local layer data.",
            run_config.image_ref,
        )
        return False
    if base_layer_missing:
        return True
    return False


def base_repository(run_config: RunConfig) -> str:
    return f"{run_config.global_cfg.image_registry}/{run_config.global_cfg.image_base_repository}"


def base_image_ref(run_config: RunConfig) -> str:
    repository = base_repository(run_config)
    return f"{repository}:{run_config.base}"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _base_layer_missing(base_image_ref: str, final_image_ref: str) -> bool | None:
    base_layers = get_local_rootfs_layers(base_image_ref)
    if base_layers is None:
        return None
    final_layers = get_local_rootfs_layers(final_image_ref)
    if final_layers is None:
        return None
    return base_layers[-1] not in final_layers
