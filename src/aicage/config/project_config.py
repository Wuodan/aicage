from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = ["ProjectConfig"]


@dataclass
class ProjectConfig:
    path: str
    tools: dict[str, dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, project_path: Path, data: dict[str, Any]) -> "ProjectConfig":
        tools = data.get("tools", {}) or {}
        legacy_docker_args = data.get("docker_args", "")
        if legacy_docker_args:
            for tool_cfg in tools.values():
                tool_cfg.setdefault("docker_args", legacy_docker_args)
        return cls(
            path=data.get("path", str(project_path)),
            tools=tools,
        )

    def to_mapping(self) -> dict[str, Any]:
        return {"path": self.path, "tools": self.tools}
