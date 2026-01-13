from dataclasses import dataclass

from aicage._logging import get_logger
from aicage.config.context import ConfigContext
from aicage.config.images_metadata.models import AgentMetadata
from aicage.constants import DEFAULT_IMAGE_BASE
from aicage.runtime.errors import RuntimeExecutionError

from ._tty import ensure_tty_for_prompt
from .base import BaseOption, available_bases, base_options


@dataclass(frozen=True)
class ExtendedImageOption:
    name: str
    base: str
    description: str
    extensions: list[str]
    image_ref: str


@dataclass(frozen=True)
class ImageChoiceRequest:
    agent: str
    context: ConfigContext
    agent_metadata: AgentMetadata
    extended_options: list[ExtendedImageOption]


@dataclass(frozen=True)
class ImageChoice:
    kind: str
    value: str


def prompt_for_image_choice(request: ImageChoiceRequest) -> ImageChoice:
    ensure_tty_for_prompt()
    logger = get_logger()
    bases = base_options(request.context, request.agent_metadata)
    extended = request.extended_options
    options = _build_image_options(bases, extended)
    prompt = _render_image_prompt(request, options)
    response = input(prompt).strip()
    choice = _parse_image_choice_response(response, request, bases, extended, options)
    logger.info("Selected %s '%s' for agent '%s'", choice.kind, choice.value, request.agent)
    return choice


def _build_image_options(
    bases: list[BaseOption],
    extended: list[ExtendedImageOption],
) -> list[tuple[str, ImageChoice]]:
    options: list[tuple[str, ImageChoice]] = []
    for option in bases:
        label = f"{option.base}: {option.description}"
        options.append((label, ImageChoice(kind="base", value=option.base)))
    for option in extended:
        extension_list = ", ".join(option.extensions)
        label = (
            f"{option.name}: {option.description} (base {option.base}, extensions: {extension_list})"
        )
        options.append((label, ImageChoice(kind="extended", value=option.name)))
    return options


def _render_image_prompt(
    request: ImageChoiceRequest,
    options: list[tuple[str, ImageChoice]],
) -> str:
    title = f"Select image for '{request.agent}' (runtime to use inside the container):"
    if not options:
        return f"{title} [{DEFAULT_IMAGE_BASE}]: "
    print(title)
    for idx, (label, choice) in enumerate(options, start=1):
        suffix = ""
        if choice.kind == "base" and choice.value == DEFAULT_IMAGE_BASE:
            suffix = " (default)"
        print(f"  {idx}) {label}{suffix}")
    return f"Enter number or name [{DEFAULT_IMAGE_BASE}]: "


def _parse_image_choice_response(
    response: str,
    request: ImageChoiceRequest,
    bases: list[BaseOption],
    extended: list[ExtendedImageOption],
    options: list[tuple[str, ImageChoice]],
) -> ImageChoice:
    if not response:
        return ImageChoice(kind="base", value=DEFAULT_IMAGE_BASE)
    if response.isdigit() and options:
        idx = int(response)
        if idx < 1 or idx > len(options):
            raise RuntimeExecutionError(
                f"Invalid choice '{response}'. Pick a number between 1 and {len(options)}."
            )
        return options[idx - 1][1]
    base_match = _match_base_choice(response, bases)
    if base_match is not None:
        return ImageChoice(kind="base", value=base_match)
    extended_match = _match_extended_choice(response, extended)
    if extended_match is None:
        valid = ", ".join(available_bases(bases) + [option.name for option in extended])
        raise RuntimeExecutionError(f"Invalid choice '{response}'. Valid options: {valid}")
    return ImageChoice(kind="extended", value=extended_match)


def _match_base_choice(response: str, options: list[BaseOption]) -> str | None:
    if response in available_bases(options):
        return response
    return None


def _match_extended_choice(response: str, options: list[ExtendedImageOption]) -> str | None:
    for option in options:
        if option.name == response:
            return option.name
    return None
