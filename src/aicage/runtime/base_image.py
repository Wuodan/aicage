import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from aicage.config.context import ConfigContext
from aicage.discovery import DiscoveryError, discover_base_aliases
from aicage.errors import CliError
from aicage.runtime.prompts import BaseSelectionRequest, prompt_for_base


@dataclass
class BaseImageSelection:
    image_ref: str
    tool_path_label: str
    tool_config_host: Path
    project_dirty: bool

__all__ = ["BaseImageSelection", "resolve_base_image"]


def _discover_local_bases(repository: str, tool: str) -> List[str]:
    """
    Fallback discovery using local images when Docker Hub is unavailable.
    """
    try:
        result = subprocess.run(
            ["docker", "image", "ls", repository, "--format", "{{.Repository}}:{{.Tag}}"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise CliError(f"Failed to list local images for {repository}: {exc.stderr or exc}") from exc

    aliases: set[str] = set()
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or line.endswith(":<none>"):
            continue
        if ":" not in line:
            continue
        repo, tag = line.split(":", 1)
        if repo != repository:
            continue
        prefix = f"{tool}-"
        suffix = "-latest"
        if tag.startswith(prefix) and tag.endswith(suffix):
            base = tag[len(prefix) : -len(suffix)]
            if base:
                aliases.add(base)

    return sorted(aliases)


def _discover_available_bases(repository: str, tool: str) -> List[str]:
    remote_bases: List[str] = []
    local_bases: List[str] = []
    try:
        remote_bases = discover_base_aliases(repository, tool)
    except DiscoveryError as exc:
        print(f"[aicage] Warning: {exc}. Continuing with local images.", file=sys.stderr)
    try:
        local_bases = _discover_local_bases(repository, tool)
    except CliError as exc:
        print(f"[aicage] Warning: {exc}", file=sys.stderr)
    return sorted(set(remote_bases) | set(local_bases))


def _pull_image(image_ref: str) -> None:
    pull_result = subprocess.run(["docker", "pull", image_ref], capture_output=True, text=True)
    if pull_result.returncode == 0:
        return

    inspect = subprocess.run(
        ["docker", "image", "inspect", image_ref],
        capture_output=True,
        text=True,
    )
    if inspect.returncode == 0:
        msg = pull_result.stderr.strip() or f"docker pull failed for {image_ref}"
        print(f"[aicage] Warning: {msg}. Using local image.", file=sys.stderr)
        return

    raise CliError(f"docker pull failed for {image_ref}: {pull_result.stderr.strip() or pull_result.stdout.strip()}")


def _read_tool_label(image_ref: str, label: str) -> str:
    try:
        result = subprocess.run(
            ["docker", "inspect", image_ref, "--format", f'{{{{ index .Config.Labels "{label}" }}}}'],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise CliError(f"Failed to inspect image {image_ref}: {exc.stderr.strip() or exc}") from exc
    value = result.stdout.strip()
    if not value:
        raise CliError(f"Label '{label}' not found on image {image_ref}.")
    return value


def resolve_base_image(tool: str, tool_cfg: Dict[str, Any], context: ConfigContext) -> BaseImageSelection:
    base = tool_cfg.get("base") or context.global_cfg.tools.get(tool, {}).get("base")
    project_dirty = False

    if not base:
        available_bases = _discover_available_bases(context.global_cfg.repository, tool)
        if not available_bases:
            raise CliError(f"No base images found for tool '{tool}' (repository={context.global_cfg.repository}).")

        request = BaseSelectionRequest(tool=tool, default_base=context.global_cfg.default_base, available=available_bases)
        base = prompt_for_base(request)
        tool_cfg["base"] = base
        project_dirty = True

    image_tag = f"{tool}-{base}-latest"
    image_ref = f"{context.global_cfg.repository}:{image_tag}"

    _pull_image(image_ref)
    tool_path_label = _read_tool_label(image_ref, "tool_path")
    tool_config_host = Path(os.path.expanduser(tool_path_label)).resolve()
    tool_config_host.mkdir(parents=True, exist_ok=True)

    return BaseImageSelection(
        image_ref=image_ref,
        tool_path_label=tool_path_label,
        tool_config_host=tool_config_host,
        project_dirty=project_dirty,
    )
