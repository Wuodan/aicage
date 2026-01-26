from pathlib import Path

from aicage.cli_types import ParsedArgs
from aicage.config.context import ConfigContext
from aicage.config.project_config import AgentConfig
from aicage.runtime.run_args import EnvVar, MountSpec

from ._docker_socket import resolve_docker_socket_mount
from ._git_config import resolve_git_config_mount
from ._git_root import resolve_git_root_mount
from ._git_support import resolve_git_support_prefs
from ._gpg import resolve_gpg_mount
from ._ssh_keys import resolve_ssh_mount


def resolve_docker_args(
    context: ConfigContext,
    agent: str,
    parsed: ParsedArgs | None,
) -> tuple[list[MountSpec], list[EnvVar]]:
    agent_cfg = context.project_cfg.agents.setdefault(agent, AgentConfig())

    project_path = Path(context.project_cfg.path)
    resolve_git_support_prefs(project_path, agent_cfg)
    git_mounts = resolve_git_config_mount(agent_cfg)
    gpg_mounts = resolve_gpg_mount(project_path, agent_cfg)
    ssh_mounts = resolve_ssh_mount(project_path, agent_cfg)
    git_root_mounts = resolve_git_root_mount(project_path, agent_cfg)
    docker_mounts, docker_env = resolve_docker_socket_mount(
        agent_cfg,
        parsed.docker_socket if parsed else False,
    )

    mounts: list[MountSpec] = []
    mounts.extend(git_mounts)
    mounts.extend(gpg_mounts)
    mounts.extend(ssh_mounts)
    mounts.extend(git_root_mounts)
    mounts.extend(docker_mounts)
    env: list[EnvVar] = []
    env.extend(docker_env)
    return mounts, env
