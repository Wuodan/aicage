import os
from dataclasses import dataclass
from pathlib import Path

from docker.errors import DockerException, ImageNotFound

from aicage.docker_client import get_docker_client
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
        client = get_docker_client()
        image = client.images.get(image_ref)
    except (ImageNotFound, DockerException) as exc:
        raise CliError(f"Failed to inspect image {image_ref}: {exc}") from exc
    labels = image.labels or {}
    value = labels.get(label, "").strip()
    if not value:
        raise CliError(f"Label '{label}' not found on image {image_ref}.")
    return value
