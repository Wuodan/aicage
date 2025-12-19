import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from aicage.config.context import ConfigContext
from aicage.errors import CliError
from aicage.runtime.prompts import BaseSelectionRequest, prompt_for_base
from .discovery.catalog import discover_tool_bases


@dataclass
class ImageSelection:
    image_ref: str
    tool_path_label: str
    tool_config_host: Path
    project_dirty: bool

__all__ = ["ImageSelection", "resolve_tool_image"]


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

    raise CliError(
        f"docker pull failed for {image_ref}: {pull_result.stderr.strip() or pull_result.stdout.strip()}"
    )


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


def resolve_tool_image(tool: str, tool_cfg: Dict[str, Any], context: ConfigContext) -> ImageSelection:
    base = tool_cfg.get("base") or context.global_cfg.tools.get(tool, {}).get("base")
    project_dirty = False
    repository_ref = f"{context.global_cfg.image_registry}/{context.global_cfg.image_repository}"

    if not base:
        available_bases = discover_tool_bases(
            context.global_cfg.image_repository,
            repository_ref,
            context.global_cfg.image_registry_api_url,
            context.global_cfg.image_registry_api_token_url,
            tool,
        )
        if not available_bases:
            raise CliError(f"No base images found for tool '{tool}' (repository={repository_ref}).")

        request = BaseSelectionRequest(
            tool=tool,
            default_base=context.global_cfg.default_image_base,
            available=available_bases,
        )
        base = prompt_for_base(request)
        tool_cfg["base"] = base
        project_dirty = True

    image_tag = f"{tool}-{base}-latest"
    image_ref = f"{repository_ref}:{image_tag}"

    _pull_image(image_ref)
    tool_path_label = _read_tool_label(image_ref, "tool_path")
    tool_config_host = Path(os.path.expanduser(tool_path_label)).resolve()
    tool_config_host.mkdir(parents=True, exist_ok=True)

    return ImageSelection(
        image_ref=image_ref,
        tool_path_label=tool_path_label,
        tool_config_host=tool_config_host,
        project_dirty=project_dirty,
    )
