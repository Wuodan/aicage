from pathlib import Path

from aicage.config.project_config import AgentConfig
from aicage.runtime.prompts import prompt_persist_docker_socket
from aicage.runtime.run_args import MountSpec

_DOCKER_SOCKET_PATH = Path("/run/docker.sock")


def resolve_docker_socket_mount(
    agent_cfg: AgentConfig,
    cli_docker_socket: bool,
) -> list[MountSpec]:
    mounts_cfg = agent_cfg.mounts
    docker_socket_enabled = cli_docker_socket or bool(mounts_cfg.docker)
    if not docker_socket_enabled:
        return []

    mounts = [
        MountSpec(
            host_path=_DOCKER_SOCKET_PATH,
            container_path=_DOCKER_SOCKET_PATH,
        )
    ]

    if cli_docker_socket and mounts_cfg.docker is None:
        if prompt_persist_docker_socket():
            mounts_cfg.docker = True

    return mounts
