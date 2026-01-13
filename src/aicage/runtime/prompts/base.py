from dataclasses import dataclass

from aicage._logging import get_logger
from aicage.config.context import ConfigContext
from aicage.config.images_metadata.models import AgentMetadata
from aicage.constants import DEFAULT_IMAGE_BASE
from aicage.runtime.errors import RuntimeExecutionError

from ._tty import ensure_tty_for_prompt


@dataclass(frozen=True)
class BaseSelectionRequest:
    agent: str
    context: ConfigContext
    agent_metadata: AgentMetadata


@dataclass(frozen=True)
class BaseOption:
    base: str
    description: str


def prompt_for_base(request: BaseSelectionRequest) -> str:
    ensure_tty_for_prompt()
    logger = get_logger()
    title = f"Select base image for '{request.agent}' (runtime to use inside the container):"
    bases = base_options(request.context, request.agent_metadata)

    if bases:
        print(title)
        for idx, option in enumerate(bases, start=1):
            suffix = " (default)" if option.base == DEFAULT_IMAGE_BASE else ""
            print(f"  {idx}) {option.base}: {option.description}{suffix}")
        prompt = f"Enter number or name [{DEFAULT_IMAGE_BASE}]: "
    else:
        prompt = f"{title} [{DEFAULT_IMAGE_BASE}]: "

    response = input(prompt).strip()
    if not response:
        choice = DEFAULT_IMAGE_BASE
    elif response.isdigit() and bases:
        idx = int(response)
        if idx < 1 or idx > len(bases):
            raise RuntimeExecutionError(
                f"Invalid choice '{response}'. Pick a number between 1 and {len(bases)}."
            )
        choice = bases[idx - 1].base
    else:
        choice = response

    if bases and choice not in available_bases(bases):
        options = ", ".join(available_bases(bases))
        raise RuntimeExecutionError(f"Invalid base '{choice}'. Valid options: {options}")
    logger.info("Selected base '%s' for agent '%s'", choice, request.agent)
    return choice


def base_options(context: ConfigContext, agent_metadata: AgentMetadata) -> list[BaseOption]:
    return [
        BaseOption(
            base=base,
            description=context.images_metadata.bases[base].base_image_description,
        )
        for base in sorted(agent_metadata.valid_bases)
    ]


def available_bases(options: list[BaseOption]) -> list[str]:
    return [option.base for option in options]
