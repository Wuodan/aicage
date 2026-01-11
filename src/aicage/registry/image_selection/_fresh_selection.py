from __future__ import annotations

from aicage.config.context import ConfigContext
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.images_metadata.models import AgentMetadata
from aicage.config.project_config import AgentConfig
from aicage.registry.errors import RegistryError
from aicage.runtime.prompts import (
    BaseSelectionRequest,
    ImageChoice,
    ImageChoiceRequest,
    prompt_for_base,
    prompt_for_image_choice,
)

from ._metadata import available_bases
from .extensions.context import ExtensionSelectionContext
from .extensions.extended_images import (
    apply_extended_selection,
    load_extended_image_options,
    resolve_extended_image,
)
from .extensions.handler import handle_extension_selection
from .models import ImageSelection


def fresh_selection(
    agent: str,
    context: ConfigContext,
    agent_metadata: AgentMetadata,
    extensions: dict[str, ExtensionMetadata],
) -> ImageSelection:
    bases = available_bases(agent, agent_metadata)
    if not bases:
        raise RegistryError(f"No base images found for agent '{agent}' in metadata.")

    extended_images = load_extended_image_options(agent, agent_metadata, extensions)
    request = ImageChoiceRequest(
        agent=agent,
        context=context,
        agent_metadata=agent_metadata,
        extended_options=extended_images,
    )
    choice = (
        prompt_for_image_choice(request)
        if extended_images
        else ImageChoice(kind="base", value=prompt_for_base(_base_request(request)))
    )
    if choice.kind == "extended":
        selected = resolve_extended_image(choice.value, extended_images)
        return apply_extended_selection(
            agent=agent,
            agent_cfg=context.project_cfg.agents.setdefault(agent, AgentConfig()),
            selected=selected,
            agent_metadata=agent_metadata,
            context=context,
        )
    base = choice.value
    agent_cfg = context.project_cfg.agents.setdefault(agent, AgentConfig())
    agent_cfg.base = base
    return handle_extension_selection(
        ExtensionSelectionContext(
            agent=agent,
            base=base,
            agent_cfg=agent_cfg,
            agent_metadata=agent_metadata,
            extensions=extensions,
            context=context,
        )
    )


def _base_request(request: ImageChoiceRequest) -> BaseSelectionRequest:
    return BaseSelectionRequest(
        agent=request.agent,
        context=request.context,
        agent_metadata=request.agent_metadata,
    )
