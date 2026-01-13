from __future__ import annotations

from aicage.config.runtime_config import RunConfig

from ._custom_base import custom_base_image_ref


def get_base_image_ref(run_config: RunConfig) -> str:
    if run_config.context.custom_bases.get(run_config.selection.base) is not None:
        return custom_base_image_ref(run_config.selection.base)
    repository = base_repository(run_config)
    return f"{repository}:{run_config.selection.base}"


def base_repository(run_config: RunConfig) -> str:
    return (
        f"{run_config.context.global_cfg.image_registry}/"
        f"{run_config.context.global_cfg.image_base_repository}"
    )
