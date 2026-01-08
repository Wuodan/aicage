from pathlib import Path

from aicage.config.project_config import AgentConfig
from aicage.runtime.prompts import prompt_mount_ssh_keys
from aicage.runtime.run_args import MountSpec

from ._signing import is_commit_signing_enabled, resolve_signing_format

_SSH_MOUNT = Path("/aicage/host/ssh")


def _default_ssh_dir() -> Path:
    return Path.home() / ".ssh"


def resolve_ssh_mount(project_path: Path, agent_cfg: AgentConfig) -> list[MountSpec]:
    if not is_commit_signing_enabled(project_path):
        return []
    if resolve_signing_format(project_path) != "ssh":
        return []

    ssh_dir = _default_ssh_dir()
    if not ssh_dir.exists():
        return []

    mounts_cfg = agent_cfg.mounts
    pref = mounts_cfg.ssh
    if pref is None:
        pref = prompt_mount_ssh_keys(ssh_dir)
        mounts_cfg.ssh = pref

    if pref:
        return [MountSpec(host_path=ssh_dir, container_path=_SSH_MOUNT)]
    return []
