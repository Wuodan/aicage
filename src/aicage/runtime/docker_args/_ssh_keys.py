from pathlib import Path

from aicage.config.project_config import AgentConfig
from aicage.paths import CONTAINER_SSH_DIR
from aicage.runtime.run_args import MountSpec

from ._git_support import resolve_ssh_dir
from ._signing import is_commit_signing_enabled, resolve_signing_format


def resolve_ssh_mount(project_path: Path, agent_cfg: AgentConfig) -> list[MountSpec]:
    if not is_commit_signing_enabled(project_path):
        return []
    if resolve_signing_format(project_path) != "ssh":
        return []

    ssh_dir = resolve_ssh_dir()
    if not ssh_dir.exists():
        return []

    mounts_cfg = agent_cfg.mounts
    if mounts_cfg.ssh:
        return [
            MountSpec(
                host_path=ssh_dir,
                container_path=CONTAINER_SSH_DIR,
            )
        ]
    return []
