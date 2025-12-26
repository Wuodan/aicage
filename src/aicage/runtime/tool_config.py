import os
from dataclasses import dataclass
from pathlib import Path

from aicage.errors import CliError
from aicage.registry.images_metadata.models import ImagesMetadata, ToolMetadata

__all__ = ["ToolConfig", "resolve_tool_config"]


@dataclass
class ToolConfig:
    tool_path: str
    tool_config_host: Path


def resolve_tool_config(tool: str, images_metadata: ImagesMetadata) -> ToolConfig:
    tool_path = _read_tool_path(tool, images_metadata)
    tool_config_host = Path(os.path.expanduser(tool_path)).resolve()
    tool_config_host.mkdir(parents=True, exist_ok=True)
    return ToolConfig(tool_path=tool_path, tool_config_host=tool_config_host)


def _read_tool_path(tool: str, images_metadata: ImagesMetadata) -> str:
    tool_metadata = _require_tool_metadata(tool, images_metadata)
    return tool_metadata.tool_path


def _require_tool_metadata(tool: str, images_metadata: ImagesMetadata) -> ToolMetadata:
    tool_metadata = images_metadata.tools.get(tool)
    if not tool_metadata:
        raise CliError(f"Tool '{tool}' is missing from images metadata.")
    return tool_metadata
