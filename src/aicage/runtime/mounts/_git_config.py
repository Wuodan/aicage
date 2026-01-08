from pathlib import Path

from aicage.config.project_config import AgentConfig
from aicage.runtime.prompts import prompt_mount_git_config
from aicage.runtime.run_args import MountSpec

from ._exec import capture_stdout

_GITCONFIG_MOUNT = Path("/aicage/host/gitconfig")


def _resolve_git_config_path() -> Path | None:
    stdout = capture_stdout(["git", "config", "--global", "--show-origin", "--list"])
    if not stdout:
        return None
    for line in stdout.splitlines():
        if not line.startswith("file:"):
            continue
        parts = line[5:].split()
        if not parts:
            continue
        return Path(parts[0]).expanduser()
    return None


def resolve_git_config_mount(agent_cfg: AgentConfig) -> list[MountSpec]:
    git_config = _resolve_git_config_path()
    if not git_config or not git_config.exists():
        return []

    mounts_cfg = agent_cfg.mounts
    pref = mounts_cfg.gitconfig
    if pref is None:
        pref = prompt_mount_git_config(git_config)
        mounts_cfg.gitconfig = pref

    if pref:
        return [MountSpec(host_path=git_config, container_path=_GITCONFIG_MOUNT)]
    return []
