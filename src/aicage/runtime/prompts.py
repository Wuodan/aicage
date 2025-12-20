import sys
from dataclasses import dataclass

from aicage.errors import CliError

__all__ = ["BaseSelectionRequest", "ensure_tty_for_prompt", "prompt_yes_no", "prompt_for_base"]


@dataclass
class BaseSelectionRequest:
    tool: str
    default_base: str
    available: list[str]


def ensure_tty_for_prompt() -> None:
    if not sys.stdin.isatty():
        raise CliError("Interactive input required but stdin is not a TTY.")


def prompt_yes_no(question: str, default: bool = False) -> bool:
    ensure_tty_for_prompt()
    suffix = "[Y/n]" if default else "[y/N]"
    response = input(f"{question} {suffix} ").strip().lower()
    if not response:
        return default
    return response in {"y", "yes"}


def prompt_for_base(request: BaseSelectionRequest) -> str:
    ensure_tty_for_prompt()
    title = f"Select base image for '{request.tool}' (runtime to use inside the container):"

    if request.available:
        print(title)
        for idx, base in enumerate(request.available, start=1):
            suffix = " (default)" if base == request.default_base else ""
            print(f"  {idx}) {base}{suffix}")
        prompt = f"Enter number or name [{request.default_base}]: "
    else:
        prompt = f"{title} [{request.default_base}]: "

    response = input(prompt).strip()
    if not response:
        choice = request.default_base
    elif response.isdigit() and request.available:
        idx = int(response)
        if idx < 1 or idx > len(request.available):
            raise CliError(f"Invalid choice '{response}'. Pick a number between 1 and {len(request.available)}.")
        choice = request.available[idx - 1]
    else:
        choice = response

    if request.available and choice not in request.available:
        options = ", ".join(request.available)
        raise CliError(f"Invalid base '{choice}'. Valid options: {options}")
    return choice
