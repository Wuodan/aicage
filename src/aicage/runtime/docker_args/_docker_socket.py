import os

from aicage.config.project_config import AgentConfig
from aicage.paths import CONTAINER_DOCKER_SOCKET_PATH, HOST_DOCKER_SOCKET_PATH
from aicage.runtime.env_vars import DOCKER_HOST, WINDOWS_DOCKER_HOST
from aicage.runtime.prompts.confirm import prompt_persist_docker_socket
from aicage.runtime.run_args import EnvVar, MountSpec


def resolve_docker_socket_mount(
    agent_cfg: AgentConfig,
    cli_docker_socket: bool,
) -> tuple[list[MountSpec], list[EnvVar]]:
    mounts_cfg = agent_cfg.mounts
    docker_socket_enabled = cli_docker_socket or bool(mounts_cfg.docker)
    if not docker_socket_enabled:
        return [], []

    if os.name == "nt":
        mounts: list[MountSpec] = []
        env = [EnvVar(name=DOCKER_HOST, value=WINDOWS_DOCKER_HOST)]
    else:
        mounts = [
            MountSpec(
                host_path=HOST_DOCKER_SOCKET_PATH,
                container_path=CONTAINER_DOCKER_SOCKET_PATH,
            )
        ]
        env = []

    if cli_docker_socket and mounts_cfg.docker is None:
        if prompt_persist_docker_socket():
            mounts_cfg.docker = True

    return mounts, env
