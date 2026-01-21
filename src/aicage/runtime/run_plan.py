from pathlib import PurePosixPath

from aicage.cli_types import ParsedArgs
from aicage.config.runtime_config import RunConfig
from aicage.paths import CONTAINER_AGENT_CONFIG_DIR
from aicage.runtime._agent_config import AgentConfig, resolve_agent_config
from aicage.runtime.run_args import DockerRunArgs, MountSpec, merge_docker_args


def build_run_args(config: RunConfig, parsed: ParsedArgs) -> DockerRunArgs:
    agent_config: AgentConfig = resolve_agent_config(
        config.context.agents[config.agent],
    )

    merged_docker_args: str = merge_docker_args(
        config.project_docker_args,
        parsed.docker_args,
    )
    agent_config_mounts = _build_agent_config_mounts(agent_config)
    return DockerRunArgs(
        image_ref=config.selection.image_ref,
        project_path=config.project_path,
        agent_config_mounts=agent_config_mounts,
        merged_docker_args=merged_docker_args,
        agent_args=parsed.agent_args,
        env=config.env,
        mounts=config.mounts,
    )


def _build_agent_config_mounts(agent_config: AgentConfig) -> list[MountSpec]:
    mounts: list[MountSpec] = []
    for agent_path, host_path in zip(agent_config.agent_path, agent_config.agent_config_host, strict=True):
        relative_path = _relative_agent_path(agent_path)
        container_path = CONTAINER_AGENT_CONFIG_DIR / relative_path
        mounts.append(MountSpec(host_path=host_path, container_path=container_path))
    return mounts


def _relative_agent_path(agent_path: str) -> PurePosixPath:
    if agent_path.startswith("~/"):
        return PurePosixPath(agent_path[2:])
    if agent_path.startswith("~\\"):
        return PurePosixPath(agent_path[2:].replace("\\", "/"))
    if agent_path.startswith("/"):
        return PurePosixPath(agent_path[1:])
    return PurePosixPath(agent_path)
