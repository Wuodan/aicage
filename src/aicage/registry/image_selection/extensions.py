from dataclasses import dataclass
from pathlib import Path

import yaml

from aicage.config.context import ConfigContext
from aicage.config.project_config import AgentConfig
from aicage.errors import CliError
from aicage.registry._extended_images import (
    ExtendedImageConfig,
    extended_image_config_path,
    load_extended_images,
    write_extended_image_config,
)
from aicage.registry._extensions import ExtensionMetadata
from aicage.registry._image_refs import local_image_ref
from aicage.registry.images_metadata.models import AgentMetadata
from aicage.runtime.prompts import (
    ExtendedImageOption,
    ExtensionOption,
    ensure_tty_for_prompt,
    prompt_for_extensions,
    prompt_for_image_ref,
)

from .models import ImageSelection


@dataclass(frozen=True)
class ExtensionSelectionContext:
    agent: str
    base: str
    agent_cfg: AgentConfig
    agent_metadata: AgentMetadata
    extensions: dict[str, ExtensionMetadata]
    context: ConfigContext


def handle_extension_selection(selection: ExtensionSelectionContext) -> ImageSelection:
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
        agent_cfg.image_ref = base_image_ref(
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
        base_image_ref=base_image_ref(
            selection.agent_metadata,
            selection.agent,
            selection.base,
            selection.context,
        ),
    )


def load_extended_image_options(
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


def resolve_extended_image(
    name: str,
    options: list[ExtendedImageOption],
) -> ExtendedImageOption:
    for option in options:
        if option.name == name:
            return option
    raise CliError(f"Unknown extended image '{name}'.")


def apply_extended_selection(
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
        base_image_ref=base_image_ref(agent_metadata, agent, selected.base, context),
    )


def ensure_extensions_exist(
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


def base_image_ref(
    agent_metadata: AgentMetadata,
    agent: str,
    base: str,
    context: ConfigContext,
) -> str:
    if agent_metadata.local_definition_dir is not None:
        return local_image_ref(context.global_cfg.local_image_repository, agent, base)
    return agent_metadata.valid_bases[base]


def _default_extended_image_ref(agent: str, base: str, extensions: list[str]) -> str:
    tag = "-".join([agent, base, *extensions]).lower().replace("/", "-")
    return f"aicage-extended:{tag}"


def _extended_image_name(image_ref: str) -> str:
    _, _, tag = image_ref.rpartition(":")
    return tag or image_ref


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
