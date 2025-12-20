from pathlib import Path
from typing import List

from aicage.config.context import ConfigContext
from aicage.cli_types import ParsedArgs
from aicage.registry import resolve_tool_image
from aicage.runtime.auth.mounts import (
    MountPreferences,
    build_auth_mounts,
    load_mount_preferences,
    store_mount_preferences,
)
from aicage.runtime.run_args import DockerRunArgs, MountSpec, merge_docker_args
from aicage.runtime.tool_config import ToolConfig, resolve_tool_config

__all__ = ["build_run_args"]


def build_run_args(context: ConfigContext, parsed: ParsedArgs) -> DockerRunArgs:
    image_ref = resolve_tool_image(parsed.tool, context)
    tool_cfg = context.project_cfg.tools.setdefault(parsed.tool, {})
    tool_config: ToolConfig = resolve_tool_config(image_ref)

    prefs: MountPreferences = load_mount_preferences(tool_cfg)
    auth_mounts: List[MountSpec]
    prefs_updated: bool
    auth_mounts, prefs_updated = build_auth_mounts(context.project_path, prefs)
    if prefs_updated:
        store_mount_preferences(tool_cfg, prefs)
        context.store.save_project(context.project_path, context.project_cfg)

    merged_docker_args: str = merge_docker_args(
        context.global_cfg.docker_args,
        tool_cfg.get("docker_args", ""),
        parsed.docker_args,
    )

    return DockerRunArgs(
        image_ref=image_ref,
        project_path=context.project_path,
        tool_config_host=tool_config.tool_config_host,
        tool_mount_container=Path("/aicage/tool-config"),
        merged_docker_args=merged_docker_args,
        tool_args=parsed.tool_args,
        tool_path=tool_config.tool_path,
        mounts=auth_mounts,
    )
