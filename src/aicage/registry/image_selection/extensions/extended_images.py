from pathlib import Path

from aicage.config.context import ConfigContext
from aicage.config.extended_images import load_extended_images
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.images_metadata.models import AgentMetadata
from aicage.config.project_config import AgentConfig
from aicage.registry.errors import RegistryError
from aicage.runtime.prompts import ExtendedImageOption

from ..models import ImageSelection
from .refs import base_image_ref


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
    raise RegistryError(f"Unknown extended image '{name}'.")


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
