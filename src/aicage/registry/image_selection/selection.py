from __future__ import annotations

from pathlib import Path

from aicage.config.context import ConfigContext
from aicage.config.project_config import AGENT_BASE_KEY, AgentConfig
from aicage.errors import CliError
from aicage.registry._extensions import ExtensionMetadata, load_extensions
from aicage.registry.images_metadata.models import AgentMetadata, ImagesMetadata
from aicage.runtime.prompts import (
    BaseSelectionRequest,
    ImageChoice,
    ImageChoiceRequest,
    prompt_for_base,
    prompt_for_image_choice,
)

from .extensions import (
    ExtensionSelectionContext,
    apply_extended_selection,
    base_image_ref,
    ensure_extensions_exist,
    handle_extension_selection,
    load_extended_image_options,
    resolve_extended_image,
)
from .models import ImageSelection


def select_agent_image(agent: str, context: ConfigContext) -> ImageSelection:
    agent_cfg = context.project_cfg.agents.setdefault(agent, AgentConfig())
    agent_metadata = _require_agent_metadata(agent, context.images_metadata)
    base = agent_cfg.base or context.global_cfg.agents.get(agent, {}).get(AGENT_BASE_KEY)
    extensions = load_extensions()

    if agent_cfg.image_ref:
        if base is None:
            return _fresh_selection(agent, context, agent_metadata, extensions)
        _validate_base(agent, base, agent_metadata)
        if agent_cfg.extensions:
            reset = ensure_extensions_exist(
                agent=agent,
                project_config_path=context.store.project_config_path(Path(context.project_cfg.path)),
                agent_cfg=agent_cfg,
                extensions=extensions,
                context=context,
            )
            if reset:
                return _fresh_selection(agent, context, agent_metadata, extensions)
        return ImageSelection(
            image_ref=agent_cfg.image_ref,
            base=base,
            extensions=list(agent_cfg.extensions),
            base_image_ref=base_image_ref(agent_metadata, agent, base, context),
        )

    if not base:
        return _fresh_selection(agent, context, agent_metadata, extensions)

    _validate_base(agent, base, agent_metadata)
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


def _require_agent_metadata(agent: str, images_metadata: ImagesMetadata) -> AgentMetadata:
    agent_metadata = images_metadata.agents.get(agent)
    if not agent_metadata:
        raise CliError(f"Agent '{agent}' is missing from images metadata.")
    return agent_metadata


def _available_bases(
    agent: str,
    agent_metadata: AgentMetadata,
) -> list[str]:
    if not agent_metadata.valid_bases:
        raise CliError(f"Agent '{agent}' does not define any valid bases.")
    return sorted(agent_metadata.valid_bases)


def _validate_base(
    agent: str,
    base: str,
    agent_metadata: AgentMetadata,
) -> None:
    if base not in agent_metadata.valid_bases:
        raise CliError(f"Base '{base}' is not valid for agent '{agent}'.")


def _fresh_selection(
    agent: str,
    context: ConfigContext,
    agent_metadata: AgentMetadata,
    extensions: dict[str, ExtensionMetadata],
) -> ImageSelection:
    available_bases = _available_bases(agent, agent_metadata)
    if not available_bases:
        raise CliError(f"No base images found for agent '{agent}' in metadata.")

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
