import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from aicage.errors import CliError

__all__ = ["ToolConfig", "resolve_tool_config"]

_TOOL_PATH_LABEL = "org.aicage.tool.tool_path"


@dataclass
class ToolConfig:
    tool_path: str
    tool_config_host: Path


def resolve_tool_config(image_ref: str) -> ToolConfig:
    tool_path = _read_image_label(image_ref, _TOOL_PATH_LABEL)
    tool_config_host = Path(os.path.expanduser(tool_path)).resolve()
    tool_config_host.mkdir(parents=True, exist_ok=True)
    return ToolConfig(tool_path=tool_path, tool_config_host=tool_config_host)


def _read_image_label(image_ref: str, label: str) -> str:
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
