from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aicage.config.context import ConfigContext
    from aicage.config.runtime_config import RunConfig

__all__ = ["pull_image", "select_agent_image"]


def pull_image(run_config: RunConfig) -> None:
    module = importlib.import_module("aicage.registry.image_pull")
    module.pull_image(run_config)


def select_agent_image(agent: str, context: ConfigContext) -> str:
    module = importlib.import_module("aicage.registry.image_selection")
    return module.select_agent_image(agent, context)
