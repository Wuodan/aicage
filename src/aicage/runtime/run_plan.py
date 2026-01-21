from aicage.cli_types import ParsedArgs
from aicage.config.runtime_config import RunConfig
from aicage.paths import CONTAINER_AGENT_CONFIG_DIR
from aicage.runtime._agent_config import AgentConfig, resolve_agent_config
from aicage.runtime.run_args import DockerRunArgs, merge_docker_args


def build_run_args(config: RunConfig, parsed: ParsedArgs) -> DockerRunArgs:
    agent_config: AgentConfig = resolve_agent_config(
        config.context.agents[config.agent],
    )

    merged_docker_args: str = merge_docker_args(
        config.project_docker_args,
        parsed.docker_args,
    )
    return DockerRunArgs(
        image_ref=config.selection.image_ref,
        project_path=config.project_path,
        agent_config_host=agent_config.agent_config_host,
        agent_config_mount_container=CONTAINER_AGENT_CONFIG_DIR,
        merged_docker_args=merged_docker_args,
        agent_args=parsed.agent_args,
        agent_path=agent_config.agent_path,
        env=config.env,
        mounts=config.mounts,
    )
