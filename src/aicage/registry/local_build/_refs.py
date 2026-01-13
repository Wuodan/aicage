from __future__ import annotations

from aicage.config.runtime_config import RunConfig
from aicage.constants import IMAGE_BASE_REPOSITORY, IMAGE_REGISTRY

from ._custom_base import custom_base_image_ref


def get_base_image_ref(run_config: RunConfig) -> str:
    if run_config.context.custom_bases.get(run_config.selection.base) is not None:
        return custom_base_image_ref(run_config.selection.base)
    repository = base_repository(run_config)
    return f"{repository}:{run_config.selection.base}"


def base_repository(_run_config: RunConfig) -> str:
    return f"{IMAGE_REGISTRY}/{IMAGE_BASE_REPOSITORY}"
