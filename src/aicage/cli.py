import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List, Sequence, Tuple

from .config_store import ConfigError, SettingsStore, load_central_config
from .discovery import DiscoveryError, discover_base_aliases


class CliError(Exception):
    """Raised for user-facing CLI errors."""


def parse_cli(argv: Sequence[str]) -> Tuple[bool, str, str, List[str]]:
    """
    Returns (dry_run, docker_args, tool, tool_args).
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

    docker_args = ""
    tool_args: List[str] = []

    if not remaining:
        raise CliError("Missing arguments. Provide a tool name (and optional docker args).")

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

    return opts.dry_run, docker_args, tool, tool_args


def ensure_tty_for_prompt() -> None:
    if not sys.stdin.isatty():
        raise CliError("Interactive input required but stdin is not a TTY.")


def prompt_for_base(tool: str, default_base: str, available: List[str]) -> str:
    ensure_tty_for_prompt()
    choices = ", ".join(available) if available else "none discovered"
    prompt = f"Select base image for '{tool}' [{default_base}] (options: {choices}): "
    response = input(prompt).strip()
    choice = response or default_base
    if available and choice not in available:
        raise CliError(f"Invalid base '{choice}'. Valid options: {choices}")
    return choice


def read_tool_label(image_ref: str, label: str) -> str:
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


def resolve_user_ids() -> List[str]:
    env_flags: List[str] = []
    try:
        uid = os.getuid()
        gid = os.getgid()
    except AttributeError:
        uid = gid = None

    user = os.environ.get("USER") or os.environ.get("USERNAME") or "aicage"
    if uid is not None:
        env_flags.extend(["-e", f"AICAGE_UID={uid}", "-e", f"AICAGE_GID={gid}"])
    env_flags.extend(["-e", f"AICAGE_USER={user}"])
    return env_flags


def assemble_docker_run(
    image_ref: str,
    project_path: Path,
    tool_config_path: Path,
    merged_docker_args: str,
    tool_args: List[str],
) -> List[str]:
    cmd: List[str] = ["docker", "run", "--rm", "-it"]
    cmd.extend(resolve_user_ids())
    cmd.extend(["-v", f"{project_path}:/workspace"])
    cmd.extend(["-v", f"{tool_config_path}:{tool_config_path}"])

    if merged_docker_args:
        cmd.extend(shlex.split(merged_docker_args))

    cmd.append(image_ref)
    cmd.extend(tool_args)
    return cmd


def pull_image(image_ref: str) -> None:
    try:
        subprocess.run(["docker", "pull", image_ref], check=True)
    except subprocess.CalledProcessError as exc:
        raise CliError(f"docker pull failed for {image_ref}: {exc.stderr or exc}") from exc


def main(argv: Sequence[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    try:
        dry_run, cli_docker_args, tool, tool_args = parse_cli(argv)
        root_config_path = Path(__file__).resolve().parents[2] / "config.yaml"
        central = load_central_config(root_config_path)
        repository = central.get("AICAGE_REPOSITORY")
        default_base = central.get("AICAGE_DEFAULT_BASE")
        if not repository:
            raise CliError("AICAGE_REPOSITORY missing from config.yaml.")
        if not default_base:
            raise CliError("AICAGE_DEFAULT_BASE missing from config.yaml.")

        project_path = Path.cwd().resolve()
        store = SettingsStore()
        global_cfg = store.load_global()
        project_cfg = store.load_project(project_path)
        tool_project_cfg = project_cfg.get("tools", {}).get(tool, {})
        tool_global_cfg = global_cfg.get("tools", {}).get(tool, {})

        base = tool_project_cfg.get("base") or tool_global_cfg.get("base")
        available_bases: List[str] = []
        if not base:
            available_bases = discover_base_aliases(repository, tool)
            base = prompt_for_base(tool, default_base, available_bases)
            tools_cfg = project_cfg.setdefault("tools", {})
            tool_entry = tools_cfg.setdefault(tool, {})
            tool_entry["base"] = base
            store.save_project(project_path, project_cfg)

        image_tag = f"{tool}-{base}-latest"
        image_ref = f"{repository}:{image_tag}"

        pull_image(image_ref)
        tool_path_label = read_tool_label(image_ref, "tool_path")
        tool_config_path = Path(os.path.expanduser(tool_path_label)).resolve()
        tool_config_path.mkdir(parents=True, exist_ok=True)

        merged_docker_args = " ".join(
            part for part in [global_cfg.get("docker_args", ""), project_cfg.get("docker_args", ""), cli_docker_args] if part
        ).strip()

        run_cmd = assemble_docker_run(
            image_ref=image_ref,
            project_path=project_path,
            tool_config_path=tool_config_path,
            merged_docker_args=merged_docker_args,
            tool_args=tool_args,
        )

        if dry_run:
            print(shlex.join(run_cmd))
            return 0

        subprocess.run(run_cmd, check=True)
        return 0
    except (CliError, ConfigError, DiscoveryError) as exc:
        print(f"[aicage] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
