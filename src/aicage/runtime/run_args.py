from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MountSpec:
    host_path: Path
    container_path: Path
    read_only: bool = False


@dataclass
class DockerRunArgs:
    image_ref: str
    project_path: Path
    agent_config_host: Path
    agent_config_mount_container: Path
    merged_docker_args: str
    agent_args: list[str]
    agent_path: str | None = None
    env: list[str] = field(default_factory=list)
    mounts: list[MountSpec] = field(default_factory=list)


def merge_docker_args(*args: str) -> str:
    return " ".join(part for part in args if part).strip()
