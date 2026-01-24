from pathlib import Path

from aicage.config.project_config import AgentConfig
from aicage.paths import container_project_path
from aicage.runtime.run_args import MountSpec

from ._git_support import resolve_git_root


def resolve_git_root_mount(project_path: Path, agent_cfg: AgentConfig) -> list[MountSpec]:
    git_root = resolve_git_root(project_path)
    if not git_root or git_root == project_path:
        return []

    mounts_cfg = agent_cfg.mounts
    if mounts_cfg.gitroot:
        return [
            MountSpec(
                host_path=git_root,
                container_path=container_project_path(git_root),
            )
        ]
    return []
