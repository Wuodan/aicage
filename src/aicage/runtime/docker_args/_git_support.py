from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from aicage.config.project_config import AgentConfig
from aicage.paths import HOST_GNUPG_DIR, HOST_SSH_DIR

from ..prompts.confirm import prompt_mount_git_support
from ._exec import capture_stdout
from ._signing import is_commit_signing_enabled, resolve_signing_format


@dataclass(frozen=True)
class _GitSupportPromptItem:
    key: str
    label: str
    path: Path


class _MountPrefs(Protocol):
    gitconfig: bool | None
    gitroot: bool | None
    gnupg: bool | None
    ssh: bool | None


def resolve_git_config_path() -> Path | None:
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


def resolve_git_root(project_path: Path) -> Path | None:
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


def resolve_gpg_home() -> Path | None:
    stdout = capture_stdout(["gpgconf", "--list-dirs", "homedir"])
    if stdout:
        path = stdout.strip()
        if path:
            gpg_home = Path(path).expanduser()
            if gpg_home.exists():
                return gpg_home
    fallback = HOST_GNUPG_DIR
    return fallback if fallback.exists() else None


def resolve_ssh_dir() -> Path:
    return HOST_SSH_DIR


def resolve_git_support_prefs(project_path: Path, agent_cfg: AgentConfig) -> None:
    mounts_cfg = agent_cfg.mounts
    items: list[_GitSupportPromptItem] = []

    git_config = resolve_git_config_path()
    if git_config and git_config.exists() and mounts_cfg.gitconfig is None:
        items.append(_GitSupportPromptItem("gitconfig", "Git config (name/email)", git_config))

    git_root = resolve_git_root(project_path)
    if git_root and git_root != project_path and mounts_cfg.gitroot is None:
        items.append(_GitSupportPromptItem("gitroot", "Git root (repository access)", git_root))

    signing_enabled = is_commit_signing_enabled(project_path)
    signing_format = resolve_signing_format(project_path) if signing_enabled else None

    if signing_enabled and signing_format == "ssh" and mounts_cfg.ssh is None:
        ssh_dir = resolve_ssh_dir()
        if ssh_dir.exists():
            items.append(
                _GitSupportPromptItem(
                    "ssh",
                    "SSH keys (for Git signing)",
                    ssh_dir,
                )
            )
    elif signing_enabled and mounts_cfg.gnupg is None:
        gpg_home = resolve_gpg_home()
        if gpg_home and gpg_home.exists():
            items.append(
                _GitSupportPromptItem(
                    "gnupg",
                    "GnuPG keys (for Git signing)",
                    gpg_home,
                )
            )

    if not items:
        return

    should_mount = prompt_mount_git_support(_format_prompt_items(items))
    for item in items:
        _set_mount_pref(mounts_cfg, item.key, should_mount)


def _format_prompt_items(items: Iterable[_GitSupportPromptItem]) -> list[tuple[str, Path]]:
    return [(item.label, item.path) for item in items]


def _set_mount_pref(mounts_cfg: _MountPrefs, key: str, value: bool) -> None:
    setattr(mounts_cfg, key, value)
