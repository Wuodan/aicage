import sys
from dataclasses import dataclass

from aicage._logging import get_logger
from aicage.config.context import ConfigContext
from aicage.errors import CliError
from aicage.registry.images_metadata.models import AgentMetadata


@dataclass(frozen=True)
class BaseSelectionRequest:
    agent: str
    context: ConfigContext
    agent_metadata: AgentMetadata


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


@dataclass(frozen=True)
class ExtensionOption:
    name: str
    description: str


def ensure_tty_for_prompt() -> None:
    if not sys.stdin.isatty():
        raise CliError("Interactive input required but stdin is not a TTY.")


def prompt_yes_no(question: str, default: bool = False) -> bool:
    ensure_tty_for_prompt()
    suffix = "[Y/n]" if default else "[y/N]"
    response = input(f"{question} {suffix} ").strip().lower()
    if not response:
        choice = default
    else:
        choice = response in {"y", "yes"}
    get_logger().info("Prompt yes/no '%s' -> %s", question, choice)
    return choice


def prompt_for_base(request: BaseSelectionRequest) -> str:
    ensure_tty_for_prompt()
    logger = get_logger()
    title = f"Select base image for '{request.agent}' (runtime to use inside the container):"
    bases = _base_options(request.context, request.agent_metadata)

    if bases:
        print(title)
        for idx, option in enumerate(bases, start=1):
            suffix = " (default)" if option.base == request.context.global_cfg.default_image_base else ""
            print(f"  {idx}) {option.base}: {option.description}{suffix}")
        prompt = f"Enter number or name [{request.context.global_cfg.default_image_base}]: "
    else:
        prompt = f"{title} [{request.context.global_cfg.default_image_base}]: "

    response = input(prompt).strip()
    if not response:
        choice = request.context.global_cfg.default_image_base
    elif response.isdigit() and bases:
        idx = int(response)
        if idx < 1 or idx > len(bases):
            raise CliError(f"Invalid choice '{response}'. Pick a number between 1 and {len(bases)}.")
        choice = bases[idx - 1].base
    else:
        choice = response

    if bases and choice not in _available_bases(bases):
        options = ", ".join(_available_bases(bases))
        raise CliError(f"Invalid base '{choice}'. Valid options: {options}")
    logger.info("Selected base '%s' for agent '%s'", choice, request.agent)
    return choice


def prompt_for_image_choice(request: ImageChoiceRequest) -> ImageChoice:
    ensure_tty_for_prompt()
    logger = get_logger()
    bases = _base_options(request.context, request.agent_metadata)
    extended = request.extended_options
    options = _build_image_options(bases, extended)
    prompt = _render_image_prompt(request, options)
    response = input(prompt).strip()
    choice = _parse_image_choice_response(response, request, bases, extended, options)
    logger.info("Selected %s '%s' for agent '%s'", choice.kind, choice.value, request.agent)
    return choice


def prompt_for_extensions(options: list[ExtensionOption]) -> list[str]:
    if not options:
        return []
    ensure_tty_for_prompt()
    print("Select extensions to add (comma-separated numbers or names, empty for none):")
    for idx, option in enumerate(options, start=1):
        print(f"  {idx}) {option.name}: {option.description}")
    response = input("Enter selection: ").strip()
    if not response:
        return []
    requested = [item.strip() for item in response.split(",") if item.strip()]
    selection: list[str] = []
    seen: set[str] = set()
    for item in requested:
        extension_id = _resolve_extension_choice(item, options)
        if extension_id in seen:
            raise CliError(f"Duplicate extension '{extension_id}' selected.")
        seen.add(extension_id)
        selection.append(extension_id)
    return selection


def prompt_for_image_ref(default_ref: str) -> str:
    ensure_tty_for_prompt()
    response = input(f"Enter image name:tag [{default_ref}]: ").strip()
    if not response:
        return default_ref
    if ":" not in response:
        return f"aicage-extended:{response}"
    return response


@dataclass(frozen=True)
class _BaseOption:
    base: str
    description: str


def _base_options(context: ConfigContext, agent_metadata: AgentMetadata) -> list[_BaseOption]:
    return [
        _BaseOption(
            base=base,
            description=context.images_metadata.bases[base].base_image_description,
        )
        for base in sorted(agent_metadata.valid_bases)
    ]


def _available_bases(options: list[_BaseOption]) -> list[str]:
    return [option.base for option in options]


def _build_image_options(
    bases: list[_BaseOption],
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
        return f"{title} [{request.context.global_cfg.default_image_base}]: "
    print(title)
    for idx, (label, choice) in enumerate(options, start=1):
        suffix = ""
        if choice.kind == "base" and choice.value == request.context.global_cfg.default_image_base:
            suffix = " (default)"
        print(f"  {idx}) {label}{suffix}")
    return f"Enter number or name [{request.context.global_cfg.default_image_base}]: "


def _parse_image_choice_response(
    response: str,
    request: ImageChoiceRequest,
    bases: list[_BaseOption],
    extended: list[ExtendedImageOption],
    options: list[tuple[str, ImageChoice]],
) -> ImageChoice:
    if not response:
        return ImageChoice(kind="base", value=request.context.global_cfg.default_image_base)
    if response.isdigit() and options:
        idx = int(response)
        if idx < 1 or idx > len(options):
            raise CliError(f"Invalid choice '{response}'. Pick a number between 1 and {len(options)}.")
        return options[idx - 1][1]
    base_match = _match_base_choice(response, bases)
    if base_match is not None:
        return ImageChoice(kind="base", value=base_match)
    extended_match = _match_extended_choice(response, extended)
    if extended_match is None:
        valid = ", ".join(_available_bases(bases) + [option.name for option in extended])
        raise CliError(f"Invalid choice '{response}'. Valid options: {valid}")
    return ImageChoice(kind="extended", value=extended_match)


def _match_base_choice(response: str, options: list[_BaseOption]) -> str | None:
    if response in _available_bases(options):
        return response
    return None


def _match_extended_choice(response: str, options: list[ExtendedImageOption]) -> str | None:
    for option in options:
        if option.name == response:
            return option.name
    return None


def _resolve_extension_choice(response: str, options: list[ExtensionOption]) -> str:
    if response.isdigit():
        idx = int(response)
        if idx < 1 or idx > len(options):
            raise CliError(f"Invalid selection '{response}'. Pick a number between 1 and {len(options)}.")
        return options[idx - 1].name
    for option in options:
        if option.name == response:
            return option.name
    valid = ", ".join(option.name for option in options)
    raise CliError(f"Invalid extension '{response}'. Valid options: {valid}")
