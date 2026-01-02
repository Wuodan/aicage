from __future__ import annotations

from pathlib import Path

from aicage.cli_types import ParsedArgs
from aicage.config.context import ConfigContext
from aicage.config.project_config import AgentConfig
from aicage.runtime.run_args import MountSpec

from ._docker_socket import resolve_docker_socket_mount
from ._entrypoint import resolve_entrypoint_mount
from ._git_config import resolve_git_config_mount
from ._gpg import resolve_gpg_mount
from ._ssh_keys import resolve_ssh_mount


def resolve_mounts(
    context: ConfigContext,
    agent: str,
    parsed: ParsedArgs | None,
) -> list[MountSpec]:
    agent_cfg = context.project_cfg.agents.setdefault(agent, AgentConfig())

    git_mounts = resolve_git_config_mount(agent_cfg)
    project_path = Path(context.project_cfg.path)
    ssh_mounts = resolve_ssh_mount(project_path, agent_cfg)
    gpg_mounts = resolve_gpg_mount(project_path, agent_cfg)
    entrypoint_mounts = resolve_entrypoint_mount(
        agent_cfg,
        parsed.entrypoint if parsed else None,
    )
    docker_mounts = resolve_docker_socket_mount(
        agent_cfg,
        parsed.docker_socket if parsed else False,
    )

    mounts: list[MountSpec] = []
    mounts.extend(git_mounts)
    mounts.extend(ssh_mounts)
    mounts.extend(gpg_mounts)
    mounts.extend(entrypoint_mounts)
    mounts.extend(docker_mounts)
    return mounts
