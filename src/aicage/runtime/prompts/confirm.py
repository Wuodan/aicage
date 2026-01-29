import os
from pathlib import Path

from aicage._logging import get_logger

from ._tty import ensure_tty_for_prompt


def _prompt_yes_no(question: str, default: bool = False) -> bool:
    ensure_tty_for_prompt()
    suffix = "[Y/n]" if default else "[y/N]"
    response = input(f"{question} {suffix} ").strip().lower()
    if not response:
        choice = default
    else:
        choice = response in {"y", "yes"}
    get_logger().info("Prompt yes/no '%s' -> %s", question, choice)
    return choice


def prompt_persist_docker_socket() -> bool:
    if os.name == "nt":
        print(
            "Info: You must enable 'Expose daemon on tcp://localhost:2375 without TLS' "
            "in Docker Desktop settings to use --docker on Windows."
        )
    return _prompt_yes_no("Persist mounting the Docker socket for this project?", default=True)


def prompt_mount_git_support(items: list[tuple[str, Path]]) -> bool:
    details = "\n".join(
        f"  - {label}: {path}"
        for label, path in items
    )
    question = f"Enable Git support in the container by mounting:\n{details}\nProceed?"
    return _prompt_yes_no(question, default=True)


def prompt_persist_docker_args(new_args: str, existing_args: str | None) -> bool:
    if existing_args:
        question = f"Persist docker run args '{new_args}' for this project (replacing '{existing_args}')?"
    else:
        question = f"Persist docker run args '{new_args}' for this project?"
    return _prompt_yes_no(question, default=True)


def prompt_update_aicage(installed_version: str, latest_version: str) -> bool:
    question = (
        "A newer version of aicage is available "
        f"(installed: {installed_version}, latest: {latest_version}). "
        "Update now?"
    )
    return _prompt_yes_no(question, default=True)
