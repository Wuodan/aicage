from __future__ import annotations

from aicage.config.runtime_config import RunConfig


def get_base_image_ref(run_config: RunConfig) -> str:
    repository = base_repository(run_config)
    return f"{repository}:{run_config.selection.base}"


def base_repository(run_config: RunConfig) -> str:
    return (
        f"{run_config.context.global_cfg.image_registry}/"
        f"{run_config.context.global_cfg.image_base_repository}"
    )
