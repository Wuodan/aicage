from pathlib import Path

from aicage.config.project_config import AgentConfig
from aicage.paths import container_project_path
from aicage.runtime.run_args import MountSpec

from ..prompts.confirm import prompt_mount_git_root
from ._exec import capture_stdout


def _resolve_git_root(project_path: Path) -> Path | None:
    superproject = _resolve_git_path(
        ["git", "rev-parse", "--show-superproject-working-tree"],
        project_path,
    )
    if superproject:
        return superproject
    return _resolve_git_path(["git", "rev-parse", "--show-toplevel"], project_path)


def _resolve_git_path(command: list[str], project_path: Path) -> Path | None:
    stdout = capture_stdout(command, cwd=project_path)
    if not stdout:
        return None
    value = stdout.strip()
    if not value:
        return None
    return Path(value).resolve()


def resolve_git_root_mount(project_path: Path, agent_cfg: AgentConfig) -> list[MountSpec]:
    git_root = _resolve_git_root(project_path)
    if not git_root or git_root == project_path:
        return []

    mounts_cfg = agent_cfg.mounts
    pref = mounts_cfg.gitroot
    if pref is None:
        pref = prompt_mount_git_root(project_path, git_root)
        mounts_cfg.gitroot = pref

    if pref:
        return [
            MountSpec(
                host_path=git_root,
                container_path=container_project_path(git_root),
            )
        ]
    return []
