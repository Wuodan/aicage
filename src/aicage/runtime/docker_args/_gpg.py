from pathlib import Path

from aicage.config.project_config import AgentConfig
from aicage.paths import CONTAINER_GNUPG_DIR
from aicage.runtime.run_args import MountSpec

from ._git_support import resolve_gpg_home
from ._signing import is_commit_signing_enabled, resolve_signing_format


def resolve_gpg_mount(project_path: Path, agent_cfg: AgentConfig) -> list[MountSpec]:
    if not is_commit_signing_enabled(project_path):
        return []
    if resolve_signing_format(project_path) == "ssh":
        return []

    gpg_home = resolve_gpg_home()
    if not gpg_home or not gpg_home.exists():
        return []

    mounts_cfg = agent_cfg.mounts
    if mounts_cfg.gnupg:
        return [
            MountSpec(
                host_path=gpg_home,
                container_path=CONTAINER_GNUPG_DIR,
            )
        ]
    return []
