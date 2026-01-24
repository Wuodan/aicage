from aicage.config.project_config import AgentConfig
from aicage.paths import CONTAINER_GITCONFIG_PATH
from aicage.runtime.run_args import MountSpec

from ._git_support import resolve_git_config_path


def resolve_git_config_mount(agent_cfg: AgentConfig) -> list[MountSpec]:
    git_config = resolve_git_config_path()
    if not git_config or not git_config.exists():
        return []

    mounts_cfg = agent_cfg.mounts
    if mounts_cfg.gitconfig:
        return [
            MountSpec(
                host_path=git_config,
                container_path=CONTAINER_GITCONFIG_PATH,
            )
        ]
    return []
