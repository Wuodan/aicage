from pathlib import Path

from aicage._logging import get_logger

from ._tty import ensure_tty_for_prompt


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


def prompt_persist_entrypoint(entrypoint_path: Path) -> bool:
    return prompt_yes_no(f"Persist entrypoint '{entrypoint_path}' for this project?", default=True)


def prompt_persist_docker_socket() -> bool:
    return prompt_yes_no("Persist mounting the Docker socket for this project?", default=True)


def prompt_mount_git_config(git_config: Path) -> bool:
    question = f"Mount Git config from '{git_config}' so Git uses your usual name/email?"
    return prompt_yes_no(question, default=True)


def prompt_mount_gpg_keys(gpg_home: Path) -> bool:
    question = f"Mount GnuPG keys from '{gpg_home}' so Git signing works like on your host?"
    return prompt_yes_no(question, default=True)


def prompt_mount_ssh_keys(ssh_dir: Path) -> bool:
    question = f"Mount SSH keys from '{ssh_dir}' so Git signing works like on your host?"
    return prompt_yes_no(question, default=True)


def prompt_persist_docker_args(new_args: str, existing_args: str | None) -> bool:
    if existing_args:
        question = f"Persist docker run args '{new_args}' for this project (replacing '{existing_args}')?"
    else:
        question = f"Persist docker run args '{new_args}' for this project?"
    return prompt_yes_no(question, default=True)
