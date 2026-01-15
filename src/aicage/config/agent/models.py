from dataclasses import dataclass, field
from pathlib import Path

AGENT_PATH_KEY: str = "agent_path"
AGENT_FULL_NAME_KEY: str = "agent_full_name"
AGENT_HOMEPAGE_KEY: str = "agent_homepage"
BUILD_LOCAL_KEY: str = "build_local"
BASE_EXCLUDE_KEY: str = "base_exclude"
BASE_DISTRO_EXCLUDE_KEY: str = "base_distro_exclude"


@dataclass(frozen=True)
class AgentMetadata:
    agent_path: str
    agent_full_name: str
    agent_homepage: str
    build_local: bool
    valid_bases: dict[str, str]
    local_definition_dir: Path
    base_exclude: list[str] = field(default_factory=list)
    base_distro_exclude: list[str] = field(default_factory=list)
