from aicage.config.project_config import AgentConfig
from aicage.paths import CONTAINER_DOCKER_SOCKET_PATH, HOST_DOCKER_SOCKET_PATH
from aicage.runtime.prompts.confirm import prompt_persist_docker_socket
from aicage.runtime.run_args import MountSpec


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
            host_path=HOST_DOCKER_SOCKET_PATH,
            container_path=CONTAINER_DOCKER_SOCKET_PATH,
        )
    ]

    if cli_docker_socket and mounts_cfg.docker is None:
        if prompt_persist_docker_socket():
            mounts_cfg.docker = True

    return mounts
