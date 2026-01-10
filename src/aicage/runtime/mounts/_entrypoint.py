import os
from pathlib import Path

from aicage.config.project_config import AgentConfig
from aicage.runtime.errors import RuntimeExecutionError
from aicage.runtime.prompts import prompt_persist_entrypoint
from aicage.runtime.run_args import MountSpec

_ENTRYPOINT_CONTAINER_PATH = Path("/usr/local/bin/entrypoint.sh")


def resolve_entrypoint_mount(
    agent_cfg: AgentConfig,
    cli_entrypoint: str | None,
) -> list[MountSpec]:
    entrypoint_value = cli_entrypoint or agent_cfg.entrypoint
    if not entrypoint_value:
        return []

    entrypoint_path = _resolve_entrypoint_path(entrypoint_value)
    _validate_entrypoint_path(entrypoint_path)
    mounts = [
        MountSpec(
            host_path=entrypoint_path,
            container_path=_ENTRYPOINT_CONTAINER_PATH,
            read_only=True,
        )
    ]

    if cli_entrypoint and agent_cfg.entrypoint is None:
        if prompt_persist_entrypoint(entrypoint_path):
            agent_cfg.entrypoint = str(entrypoint_path)

    return mounts


def _resolve_entrypoint_path(entrypoint: str) -> Path:
    return Path(entrypoint).expanduser().resolve()


def _validate_entrypoint_path(path: Path) -> None:
    if not path.exists() or not path.is_file():
        raise RuntimeExecutionError(f"Entrypoint '{path}' does not exist or is not a file.")
    if os.name != "nt" and not os.access(path, os.X_OK):
        raise RuntimeExecutionError(f"Entrypoint '{path}' is not executable.")
