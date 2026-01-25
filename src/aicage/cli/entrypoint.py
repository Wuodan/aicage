import sys
from collections.abc import Sequence
from pathlib import Path

from aicage._logging import get_logger
from aicage.cli._errors import CliError
from aicage.cli._parse import parse_cli
from aicage.cli._print_config import print_project_config
from aicage.cli_types import ParsedArgs
from aicage.config.runtime_config import RunConfig, load_run_config
from aicage.docker.run import print_run_command, run_container
from aicage.errors import AicageError
from aicage.registry.ensure_image import ensure_image
from aicage.runtime.run_args import DockerRunArgs
from aicage.runtime.run_plan import build_run_args


def main(argv: Sequence[str] | None = None) -> int:
    parsed_argv: Sequence[str] = argv if argv is not None else sys.argv[1:]
    logger = get_logger()
    try:
        parsed: ParsedArgs = parse_cli(parsed_argv)
        if parsed.config_action == "print":
            print_project_config()
            return 0
        run_config: RunConfig = load_run_config(parsed.agent, parsed)
        _validate_home_mount_safety(run_config)
        logger.info("Resolved run config for agent %s", run_config.agent)
        ensure_image(run_config)
        run_args: DockerRunArgs = build_run_args(config=run_config, parsed=parsed)

        if parsed.dry_run:
            print_run_command(run_args)
            logger.info("Dry-run docker command printed.")
            return 0

        run_container(run_args)
        return 0
    except KeyboardInterrupt:
        print()
        logger.warning("Interrupted by user.")
        return 130
    except AicageError as exc:
        print(f"[aicage] {exc}", file=sys.stderr)
        logger.error("CLI error: %s", exc)
        return 1


def _validate_home_mount_safety(run_config: RunConfig) -> None:
    home_path = _resolve_home_path()
    if _is_parent_or_same(run_config.project_path, home_path):
        raise CliError(
            "Refusing to start: this would mount your home directory into the container.",
        )
    for mount in run_config.mounts:
        if _is_parent_or_same(mount.host_path, home_path):
            raise CliError(
                "Refusing to start: this would mount your home directory into the container.",
            )


def _resolve_home_path() -> Path:
    return Path.home().resolve()


def _is_parent_or_same(path: Path, home_path: Path) -> bool:
    candidate = path.resolve()
    return candidate == home_path or candidate in home_path.parents
