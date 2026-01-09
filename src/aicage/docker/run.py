from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path

from aicage.runtime.env_vars import (
    AICAGE_AGENT_CONFIG_PATH,
    AICAGE_GID,
    AICAGE_UID,
    AICAGE_USER,
    AICAGE_WORKSPACE,
)
from aicage.runtime.run_args import DockerRunArgs


def run_container(args: DockerRunArgs) -> None:
    command = _assemble_docker_run(args)
    subprocess.run(command, check=True)


def print_run_command(args: DockerRunArgs) -> None:
    command = _assemble_docker_run(args)
    print(shlex.join(command))


def run_builder_version_check(image_ref: str, definition_dir: Path) -> subprocess.CompletedProcess[str]:
    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{definition_dir.resolve()}:/agent:ro",
        "-w",
        "/agent",
        image_ref,
        "/bin/bash",
        "/agent/version.sh",
    ]
    return subprocess.run(command, check=False, capture_output=True, text=True)


def _resolve_user_ids() -> list[str]:
    env_flags: list[str] = []
    try:
        uid = os.getuid()
        gid = os.getgid()
    except AttributeError:
        uid = gid = None

    user = os.environ.get("USER") or os.environ.get("USERNAME") or "aicage"
    if uid is not None:
        env_flags.extend(["-e", f"{AICAGE_UID}={uid}", "-e", f"{AICAGE_GID}{'='}{gid}"])
    env_flags.extend(["-e", f"{AICAGE_USER}={user}"])
    return env_flags


def _assemble_docker_run(args: DockerRunArgs) -> list[str]:
    cmd: list[str] = ["docker", "run", "--rm", "-it"]
    cmd.extend(_resolve_user_ids())
    cmd.extend(["-e", f"{AICAGE_WORKSPACE}={args.project_path}"])
    if args.agent_path:
        cmd.extend(["-e", f"{AICAGE_AGENT_CONFIG_PATH}={args.agent_path}"])
    for env in args.env:
        cmd.extend(["-e", env])
    cmd.extend(["-v", f"{args.project_path}:/workspace"])
    cmd.extend(["-v", f"{args.project_path}:{args.project_path}"])
    cmd.extend(["-v", f"{args.agent_config_host}:{args.agent_config_mount_container}"])
    for mount in args.mounts:
        suffix = ":ro" if mount.read_only else ""
        cmd.extend(["-v", f"{mount.host_path}:{mount.container_path}{suffix}"])

    if args.merged_docker_args:
        cmd.extend(shlex.split(args.merged_docker_args))

    cmd.append(args.image_ref)
    cmd.extend(args.agent_args)
    return cmd
