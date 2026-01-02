from __future__ import annotations

from datetime import datetime, timezone

from aicage.config.runtime_config import RunConfig

from ._runner import local_image_exists
from ._store import BuildRecord


def should_build(
    run_config: RunConfig,
    record: BuildRecord | None,
    base_digest: str | None,
) -> bool:
    if not local_image_exists(run_config.image_ref):
        return True
    if record is None:
        return True
    if record.agent_version != run_config.agent_version:
        return True
    if record.base_digest is None:
        return True
    if base_digest and record.base_digest != base_digest:
        return True
    return False


def base_repository(run_config: RunConfig) -> str:
    return f"{run_config.global_cfg.image_registry}/{run_config.global_cfg.image_base_repository}"


def base_image_ref(run_config: RunConfig) -> str:
    repository = base_repository(run_config)
    return f"{repository}:{run_config.base}"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
