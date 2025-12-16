import argparse
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

from aicage.config import ConfigError
from aicage.config.context import build_config_context
from aicage.discovery import DiscoveryError
from aicage.errors import CliError
from aicage.runtime.base_image import BaseImageSelection, resolve_base_image
from aicage.runtime.auth.mounts import (
    build_auth_mounts,
    load_mount_preferences,
    store_mount_preferences,
)
from aicage.runtime.run_args import DockerRunArgs, assemble_docker_run, merge_docker_args

_TOOL_MOUNT_CONTAINER = Path("/aicage/tool-config")

__all__ = ["ParsedArgs", "parse_cli", "main"]


@dataclass
class ParsedArgs:
    dry_run: bool
    docker_args: str
    tool: str
    tool_args: List[str]


def parse_cli(argv: Sequence[str]) -> ParsedArgs:
    """
    Returns parsed CLI args.
    Docker args are a single opaque string; precedence is resolved later.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--dry-run", action="store_true", help="Print docker run command without executing.")
    parser.add_argument("-h", "--help", action="store_true", help="Show help message and exit.")
    opts, remaining = parser.parse_known_args(argv)

    if opts.help:
        usage = (
            "Usage:\n"
            "  aicage [--dry-run] [<docker-args>] <tool> [-- <tool-args>]\n"
            "  aicage [--dry-run] [<docker-args>] -- <tool> <tool-args>\n\n"
            "<docker-args> is a single string of docker run flags (optional).\n"
            "<tool-args> are passed verbatim to the tool.\n"
        )
        print(usage)
        sys.exit(0)

    if not remaining:
        raise CliError("Missing arguments. Provide a tool name (and optional docker args).")

    docker_args = ""

    if "--" in remaining:
        sep_index = remaining.index("--")
        pre = remaining[:sep_index]
        post = remaining[sep_index + 1 :]
        if not post:
            raise CliError("Missing tool after '--'.")
        docker_args = " ".join(pre).strip()
        tool = post[0]
        tool_args = post[1:]
    else:
        first = remaining[0]
        if len(remaining) >= 2 and (first.startswith("-") or "=" in first):
            docker_args = first
            tool = remaining[1]
            tool_args = remaining[2:]
        else:
            tool = first
            tool_args = remaining[1:]

    if not tool:
        raise CliError("Tool name is required.")

    return ParsedArgs(opts.dry_run, docker_args, tool, tool_args)


def main(argv: Sequence[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    try:
        parsed = parse_cli(argv)
        context = build_config_context()
        tool_cfg = context.project_cfg.tools.setdefault(parsed.tool, {})

        base_selection: BaseImageSelection = resolve_base_image(parsed.tool, tool_cfg, context)

        merged_docker_args = merge_docker_args(
            context.global_cfg.docker_args, context.project_cfg.docker_args, parsed.docker_args
        )

        prefs = load_mount_preferences(tool_cfg)
        auth_mounts, prefs_updated = build_auth_mounts(context.project_path, prefs)
        if prefs_updated:
            store_mount_preferences(tool_cfg, prefs)
        project_dirty = base_selection.project_dirty or prefs_updated

        run_args = DockerRunArgs(
            image_ref=base_selection.image_ref,
            project_path=context.project_path,
            tool_config_host=base_selection.tool_config_host,
            tool_mount_container=_TOOL_MOUNT_CONTAINER,
            merged_docker_args=merged_docker_args,
            tool_args=parsed.tool_args,
            tool_path_label=base_selection.tool_path_label,
            mounts=auth_mounts,
        )

        if project_dirty:
            context.store.save_project(context.project_path, context.project_cfg)

        run_cmd = assemble_docker_run(run_args)

        if parsed.dry_run:
            print(shlex.join(run_cmd))
            return 0

        subprocess.run(run_cmd, check=True)
        return 0
    except KeyboardInterrupt:
        print()
        return 130
    except (CliError, ConfigError, DiscoveryError) as exc:
        print(f"[aicage] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
