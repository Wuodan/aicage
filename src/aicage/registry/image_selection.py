from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from aicage.config.context import ConfigContext
from aicage.config.project_config import AGENT_BASE_KEY, AgentConfig
from aicage.errors import CliError
from aicage.registry._extended_images import (
    ExtendedImageConfig,
    extended_image_config_path,
    load_extended_images,
    write_extended_image_config,
)
from aicage.registry._extensions import ExtensionMetadata, load_extensions
from aicage.registry.images_metadata.models import AgentMetadata, ImagesMetadata
from aicage.runtime.prompts import (
    BaseSelectionRequest,
    ExtendedImageOption,
    ExtensionOption,
    ImageChoice,
    ImageChoiceRequest,
    ensure_tty_for_prompt,
    prompt_for_base,
    prompt_for_extensions,
    prompt_for_image_choice,
    prompt_for_image_ref,
)

from ._image_refs import local_image_ref


@dataclass(frozen=True)
class ImageSelection:
    image_ref: str
    base: str
    extensions: list[str]
    base_image_ref: str


@dataclass(frozen=True)
class _ExtensionSelectionContext:
    agent: str
    base: str
    agent_cfg: AgentConfig
    agent_metadata: AgentMetadata
    extensions: dict[str, ExtensionMetadata]
    context: ConfigContext


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
            reset = _ensure_extensions_exist(
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
            base_image_ref=_base_image_ref(agent_metadata, agent, base, context),
        )

    if not base:
        return _fresh_selection(agent, context, agent_metadata, extensions)

    _validate_base(agent, base, agent_metadata)
    return _handle_extension_selection(
        _ExtensionSelectionContext(
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

    extended_images = _load_extended_images(agent, agent_metadata, extensions)
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
        selected = _resolve_extended_image(choice.value, extended_images)
        return _apply_extended_selection(
            agent=agent,
            agent_cfg=context.project_cfg.agents.setdefault(agent, AgentConfig()),
            selected=selected,
            agent_metadata=agent_metadata,
            context=context,
        )
    base = choice.value
    agent_cfg = context.project_cfg.agents.setdefault(agent, AgentConfig())
    agent_cfg.base = base
    return _handle_extension_selection(
        _ExtensionSelectionContext(
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


def _handle_extension_selection(selection: _ExtensionSelectionContext) -> ImageSelection:
    agent_cfg = selection.agent_cfg
    agent_cfg.base = selection.base
    extension_options = [
        ExtensionOption(
            name=ext.extension_id,
            description=f"{ext.name}: {ext.description}",
        )
        for ext in sorted(selection.extensions.values(), key=lambda item: item.extension_id)
    ]
    selected_extensions = prompt_for_extensions(extension_options) if extension_options else []
    if selected_extensions:
        image_ref = prompt_for_image_ref(
            _default_extended_image_ref(selection.agent, selection.base, selected_extensions)
        )
        agent_cfg.extensions = list(selected_extensions)
        agent_cfg.image_ref = image_ref
        write_extended_image_config(
            ExtendedImageConfig(
                name=_extended_image_name(image_ref),
                agent=selection.agent,
                base=selection.base,
                extensions=list(selected_extensions),
                image_ref=image_ref,
                path=extended_image_config_path(_extended_image_name(image_ref)),
            )
        )
    else:
        agent_cfg.extensions = []
        agent_cfg.image_ref = _base_image_ref(
            selection.agent_metadata,
            selection.agent,
            selection.base,
            selection.context,
        )
    selection.context.store.save_project(
        Path(selection.context.project_cfg.path),
        selection.context.project_cfg,
    )
    return ImageSelection(
        image_ref=agent_cfg.image_ref or "",
        base=selection.base,
        extensions=list(agent_cfg.extensions),
        base_image_ref=_base_image_ref(
            selection.agent_metadata,
            selection.agent,
            selection.base,
            selection.context,
        ),
    )


def _base_image_ref(
    agent_metadata: AgentMetadata,
    agent: str,
    base: str,
    context: ConfigContext,
) -> str:
    if agent_metadata.local_definition_dir is not None:
        return local_image_ref(context.global_cfg.local_image_repository, agent, base)
    return agent_metadata.valid_bases[base]


def _load_extended_images(
    agent: str,
    agent_metadata: AgentMetadata,
    extensions: dict[str, ExtensionMetadata],
) -> list[ExtendedImageOption]:
    configs = load_extended_images(set(extensions))
    options: list[ExtendedImageOption] = []
    for config in configs.values():
        if config.agent != agent:
            continue
        if config.base not in agent_metadata.valid_bases:
            continue
        options.append(
            ExtendedImageOption(
                name=config.name,
                base=config.base,
                description="Custom extended image",
                extensions=list(config.extensions),
                image_ref=config.image_ref,
            )
        )
    return options


def _resolve_extended_image(
    name: str,
    options: list[ExtendedImageOption],
) -> ExtendedImageOption:
    for option in options:
        if option.name == name:
            return option
    raise CliError(f"Unknown extended image '{name}'.")


def _apply_extended_selection(
    agent: str,
    agent_cfg: AgentConfig,
    selected: ExtendedImageOption,
    agent_metadata: AgentMetadata,
    context: ConfigContext,
) -> ImageSelection:
    agent_cfg.base = selected.base
    agent_cfg.extensions = list(selected.extensions)
    agent_cfg.image_ref = selected.image_ref
    context.store.save_project(Path(context.project_cfg.path), context.project_cfg)
    return ImageSelection(
        image_ref=selected.image_ref,
        base=selected.base,
        extensions=list(selected.extensions),
        base_image_ref=_base_image_ref(agent_metadata, agent, selected.base, context),
    )


def _default_extended_image_ref(agent: str, base: str, extensions: list[str]) -> str:
    tag = "-".join([agent, base, *extensions]).lower().replace("/", "-")
    return f"aicage-extended:{tag}"


def _extended_image_name(image_ref: str) -> str:
    _, _, tag = image_ref.rpartition(":")
    return tag or image_ref


def _ensure_extensions_exist(
    agent: str,
    project_config_path: Path,
    agent_cfg: AgentConfig,
    extensions: dict[str, ExtensionMetadata],
    context: ConfigContext,
) -> bool:
    missing = [ext for ext in agent_cfg.extensions if ext not in extensions]
    if not missing:
        return False
    reset = _handle_missing_extensions(agent, project_config_path, agent_cfg, context, missing)
    if reset:
        return True
    return False


def _handle_missing_extensions(
    agent: str,
    project_config_path: Path,
    agent_cfg: AgentConfig,
    context: ConfigContext,
    missing: list[str],
) -> bool:
    ensure_tty_for_prompt()
    print(f"[aicage] Missing extensions for '{agent}': {', '.join(sorted(missing))}.")
    if agent_cfg.image_ref:
        print(f"[aicage] Stored image ref: {agent_cfg.image_ref}")
    print(f"[aicage] Project config: {project_config_path}")
    _print_projects_using_image(context, agent_cfg.image_ref or "")
    choice = input("Choose 'exit' or 'fresh': ").strip().lower()
    if choice == "fresh":
        context.project_cfg.agents.pop(agent, None)
        context.store.save_project(Path(context.project_cfg.path), context.project_cfg)
        return True
    if choice == "exit":
        raise CliError("Invalid extension configuration; run aborted.")
    raise CliError("Invalid choice; run aborted.")


def _print_projects_using_image(context: ConfigContext, image_ref: str) -> None:
    if not image_ref:
        return
    store = context.store
    matches = []
    for path in sorted(store.projects_dir.glob("*.yaml")):
        data = _load_yaml(path)
        if not isinstance(data, dict):
            continue
        project_path = data.get("path", "")
        agents = data.get("agents", {}) or {}
        if not isinstance(agents, dict):
            continue
        for cfg in agents.values():
            if isinstance(cfg, dict) and cfg.get("image_ref") == image_ref:
                matches.append((project_path, path))
                break
    if not matches:
        return
    print("[aicage] Other projects using this image:")
    for project_path, config_path in matches:
        print(f"  {project_path} -> {config_path}")


def _load_yaml(path: Path) -> dict[str, object]:
    try:
        payload = path.read_text(encoding="utf-8")
        data = yaml.safe_load(payload) or {}
    except (OSError, yaml.YAMLError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data
