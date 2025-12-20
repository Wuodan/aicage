from dataclasses import dataclass
from typing import List

__all__ = ["ParsedArgs"]


@dataclass
class ParsedArgs:
    dry_run: bool
    docker_args: str
    tool: str
    tool_args: List[str]
