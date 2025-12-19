import subprocess
import sys
from dataclasses import dataclass

from aicage.config.context import ConfigContext
from aicage.errors import CliError
from aicage.runtime.prompts import BaseSelectionRequest, prompt_for_base
from .discovery.catalog import discover_tool_bases


@dataclass
class ImageSelection:
    image_ref: str
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


def resolve_tool_image(tool: str, context: ConfigContext) -> ImageSelection:
    tool_cfg = context.project_cfg.tools.setdefault(tool, {})
    base = tool_cfg.get("base") or context.global_cfg.tools.get(tool, {}).get("base")
    project_dirty = False
    repository_ref = context.image_repository_ref()

    if not base:
        available_bases = discover_tool_bases(context, tool)
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

    return ImageSelection(
        image_ref=image_ref,
        project_dirty=project_dirty,
    )
