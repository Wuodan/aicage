import argparse
import sys
from typing import List, Sequence

from aicage.cli_types import ParsedArgs
from aicage.errors import CliError

__all__ = ["parse_cli"]


def parse_cli(argv: Sequence[str]) -> ParsedArgs:
    """
    Returns parsed CLI args.
    Docker args are a single opaque string; precedence is resolved later.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--dry-run", action="store_true", help="Print docker run command without executing.")
    parser.add_argument("-h", "--help", action="store_true", help="Show help message and exit.")
    opts: argparse.Namespace
    remaining: List[str]
    opts, remaining = parser.parse_known_args(argv)

    if opts.help:
        usage: str = (
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

    docker_args: str = ""

    if "--" in remaining:
        sep_index: int = remaining.index("--")
        pre: List[str] = remaining[:sep_index]
        post: List[str] = remaining[sep_index + 1 :]
        if not post:
            raise CliError("Missing tool after '--'.")
        docker_args = " ".join(pre).strip()
        tool: str = post[0]
        tool_args: List[str] = post[1:]
    else:
        first: str = remaining[0]
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
