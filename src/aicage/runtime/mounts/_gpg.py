from pathlib import Path

from aicage.config.project_config import AgentConfig
from aicage.runtime.prompts import prompt_mount_gpg_keys
from aicage.runtime.run_args import MountSpec

from ._exec import capture_stdout
from ._signing import is_commit_signing_enabled, resolve_signing_format

_GPG_HOME_MOUNT = Path("/aicage/host/gnupg")


def _resolve_gpg_home() -> Path | None:
    stdout = capture_stdout(["gpgconf", "--list-dirs", "homedir"])
    if not stdout:
        return None
    path = stdout.strip()
    return Path(path).expanduser() if path else None


def resolve_gpg_mount(project_path: Path, agent_cfg: AgentConfig) -> list[MountSpec]:
    if not is_commit_signing_enabled(project_path):
        return []
    if resolve_signing_format(project_path) == "ssh":
        return []

    gpg_home = _resolve_gpg_home()
    if not gpg_home or not gpg_home.exists():
        return []

    mounts_cfg = agent_cfg.mounts
    pref = mounts_cfg.gnupg
    if pref is None:
        pref = prompt_mount_gpg_keys(gpg_home)
        mounts_cfg.gnupg = pref

    if pref:
        return [MountSpec(host_path=gpg_home, container_path=_GPG_HOME_MOUNT)]
    return []
