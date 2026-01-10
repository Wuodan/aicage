import sys

from aicage.runtime.errors import RuntimeExecutionError


def ensure_tty_for_prompt() -> None:
    if not sys.stdin.isatty():
        raise RuntimeExecutionError("Interactive input required but stdin is not a TTY.")
