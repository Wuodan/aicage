from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from aicage.runtime.run_args import MountSpec
from aicage.runtime import _env_vars

from ._git_config import resolve_git_config_path
from ._gpg import resolve_gpg_home
from .prompts import prompt_yes_no
from ._signing import is_commit_signing_enabled, resolve_signing_format
from ._ssh_keys import default_ssh_dir

GITCONFIG_MOUNT = Path("/aicage/host/gitconfig")
GPG_HOME_MOUNT = Path("/aicage/host/gnupg")
SSH_MOUNT = Path("/aicage/host/ssh")


@dataclass
class MountPreferences:
    gitconfig: bool | None = None
    gnupg: bool | None = None
    ssh: bool | None = None

    @classmethod
    def from_mapping(cls, data: Dict[str, Any]) -> "MountPreferences":
        return cls(
            gitconfig=data.get("gitconfig"),
            gnupg=data.get("gnupg"),
            ssh=data.get("ssh"),
        )

    def to_mapping(self) -> Dict[str, bool]:
        payload: Dict[str, bool] = {}
        if self.gitconfig is not None:
            payload["gitconfig"] = self.gitconfig
        if self.gnupg is not None:
            payload["gnupg"] = self.gnupg
        if self.ssh is not None:
            payload["ssh"] = self.ssh
        return payload


def load_mount_preferences(tool_cfg: Dict[str, Any]) -> MountPreferences:
    return MountPreferences.from_mapping(tool_cfg.get("mounts", {}))


def store_mount_preferences(tool_cfg: Dict[str, Any], prefs: MountPreferences) -> None:
    tool_cfg["mounts"] = prefs.to_mapping()


def _home_relative_target(host_path: Path, default_relative: str) -> str:
    host_home = Path.home().resolve()
    try:
        relative = host_path.resolve().relative_to(host_home)
    except ValueError:
        return default_relative
    return f"~/{relative}"


def build_auth_mounts(project_path: Path, prefs: MountPreferences) -> Tuple[List[MountSpec], List[str], bool]:
    mounts: List[MountSpec] = []
    env: List[str] = []
    updated = False

    git_config = resolve_git_config_path()
    if git_config and git_config.exists():
        if prefs.gitconfig is None:
            prefs.gitconfig = prompt_yes_no(f"Mount Git config from '{git_config}'?", default=False)
            updated = True
        if prefs.gitconfig:
            target = _home_relative_target(git_config, "~/.gitconfig")
            mounts.append(MountSpec(host_path=git_config, container_path=GITCONFIG_MOUNT))
            env.append(f"{_env_vars.AICAGE_GITCONFIG_TARGET}={target}")

    if is_commit_signing_enabled(project_path):
        signing_format = resolve_signing_format(project_path)
        if signing_format == "ssh":
            ssh_dir = default_ssh_dir()
            if ssh_dir.exists():
                if prefs.ssh is None:
                    prefs.ssh = prompt_yes_no(f"Mount SSH directory '{ssh_dir}' for Git signing?", default=False)
                    updated = True
                if prefs.ssh:
                    target = _home_relative_target(ssh_dir, "~/.ssh")
                    mounts.append(MountSpec(host_path=ssh_dir, container_path=SSH_MOUNT))
                    env.append(f"{_env_vars.AICAGE_SSH_TARGET}={target}")
        else:
            gpg_home = resolve_gpg_home()
            if gpg_home and gpg_home.exists():
                if prefs.gnupg is None:
                    prefs.gnupg = prompt_yes_no(f"Mount GnuPG home '{gpg_home}' for Git signing?", default=False)
                    updated = True
                if prefs.gnupg:
                    target = _home_relative_target(gpg_home, "~/.gnupg")
                    mounts.append(MountSpec(host_path=gpg_home, container_path=GPG_HOME_MOUNT))
                    env.extend(
                        [
                            f"{_env_vars.AICAGE_GNUPG_TARGET}={target}",
                            f"{_env_vars.GNUPGHOME}={target}",
                        ]
                    )

    return mounts, env, updated
