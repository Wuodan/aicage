from __future__ import annotations

from datetime import datetime, timezone

from aicage._logging import get_logger
from aicage.config.runtime_config import RunConfig
from aicage.docker.query import local_image_exists
from aicage.registry.layers import base_layer_missing

from ._store import BuildRecord


def should_build(
    run_config: RunConfig,
    record: BuildRecord | None,
    base_image_ref: str,
    agent_version: str,
    image_ref: str,
) -> bool:
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


def base_repository(run_config: RunConfig) -> str:
    return (
        f"{run_config.context.global_cfg.image_registry}/"
        f"{run_config.context.global_cfg.image_base_repository}"
    )


def base_image_ref(run_config: RunConfig) -> str:
    repository = base_repository(run_config)
    return f"{repository}:{run_config.selection.base}"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
