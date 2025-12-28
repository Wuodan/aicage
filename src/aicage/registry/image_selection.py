from __future__ import annotations

from pathlib import Path

from aicage.config.context import ConfigContext
from aicage.config.project_config import AgentConfig
from aicage.errors import CliError
from aicage.registry.images_metadata.models import AgentMetadata, ImagesMetadata
from aicage.runtime.prompts import BaseSelectionRequest, prompt_for_base

__all__ = ["select_agent_image"]


def select_agent_image(agent: str, context: ConfigContext) -> str:
    agent_cfg = context.project_cfg.agents.setdefault(agent, AgentConfig())
    agent_metadata = _require_agent_metadata(agent, context.images_metadata)
    base = agent_cfg.base or context.global_cfg.agents.get(agent, {}).get("base")

    if not base:
        available_bases = _available_bases(agent, agent_metadata, context.images_metadata)
        if not available_bases:
            raise CliError(f"No base images found for agent '{agent}' in metadata.")

        request = BaseSelectionRequest(
            agent=agent,
            context=context,
            agent_metadata=agent_metadata,
        )
        base = prompt_for_base(request)
        agent_cfg.base = base
        context.store.save_project(Path(context.project_cfg.path), context.project_cfg)
    else:
        _validate_base(agent, base, agent_metadata, context.images_metadata)

    image_tag = f"{agent}-{base}-latest"
    image_ref = f"{context.image_repository_ref()}:{image_tag}"
    return image_ref


def _require_agent_metadata(agent: str, images_metadata: ImagesMetadata) -> AgentMetadata:
    agent_metadata = images_metadata.agents.get(agent)
    if not agent_metadata:
        raise CliError(f"Agent '{agent}' is missing from images metadata.")
    return agent_metadata


def _available_bases(
    agent: str,
    agent_metadata: AgentMetadata,
    images_metadata: ImagesMetadata,
) -> list[str]:
    invalid = [base for base in agent_metadata.valid_bases if base not in images_metadata.bases]
    if invalid:
        raise CliError(
            f"Agent '{agent}' references unknown base(s) in metadata: {', '.join(invalid)}."
        )
    return sorted(set(agent_metadata.valid_bases))


def _validate_base(
    agent: str,
    base: str,
    agent_metadata: AgentMetadata,
    images_metadata: ImagesMetadata,
) -> None:
    if base not in agent_metadata.valid_bases:
        raise CliError(f"Base '{base}' is not valid for agent '{agent}'.")
    if base not in images_metadata.bases:
        raise CliError(f"Base '{base}' is missing from images metadata.")
