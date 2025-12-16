import sys

from aicage.errors import CliError


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
