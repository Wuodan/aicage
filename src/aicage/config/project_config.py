from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = ["ProjectConfig", "AgentConfig", "AgentMounts"]


@dataclass
class AgentMounts:
    gitconfig: bool | None = None
    gnupg: bool | None = None
    ssh: bool | None = None
    docker: bool | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "AgentMounts":
        return cls(
            gitconfig=data.get("gitconfig"),
            gnupg=data.get("gnupg"),
            ssh=data.get("ssh"),
            docker=data.get("docker"),
        )

    def to_mapping(self) -> dict[str, bool]:
        payload: dict[str, bool] = {}
        if self.gitconfig is not None:
            payload["gitconfig"] = self.gitconfig
        if self.gnupg is not None:
            payload["gnupg"] = self.gnupg
        if self.ssh is not None:
            payload["ssh"] = self.ssh
        if self.docker is not None:
            payload["docker"] = self.docker
        return payload


@dataclass
class AgentConfig:
    base: str | None = None
    docker_args: str = ""
    entrypoint: str | None = None
    mounts: AgentMounts = field(default_factory=AgentMounts)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "AgentConfig":
        mounts = AgentMounts.from_mapping(data.get("mounts", {}) or {})
        return cls(
            base=data.get("base"),
            docker_args=data.get("docker_args", "") or "",
            entrypoint=data.get("entrypoint"),
            mounts=mounts,
        )

    def to_mapping(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.base:
            payload["base"] = self.base
        if self.docker_args:
            payload["docker_args"] = self.docker_args
        if self.entrypoint:
            payload["entrypoint"] = self.entrypoint
        mounts = self.mounts.to_mapping()
        if mounts:
            payload["mounts"] = mounts
        return payload


@dataclass
class ProjectConfig:
    path: str
    agents: dict[str, AgentConfig] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, project_path: Path, data: dict[str, Any]) -> "ProjectConfig":
        raw_agents = data.get("agents", {}) or {}
        agents = {name: AgentConfig.from_mapping(cfg) for name, cfg in raw_agents.items()}
        legacy_docker_args = data.get("docker_args", "")
        if legacy_docker_args:
            for agent_cfg in agents.values():
                if not agent_cfg.docker_args:
                    agent_cfg.docker_args = legacy_docker_args
        return cls(
            path=data.get("path", str(project_path)),
            agents=agents,
        )

    def to_mapping(self) -> dict[str, Any]:
        agents_payload = {name: cfg.to_mapping() for name, cfg in self.agents.items()}
        return {"path": self.path, "agents": agents_payload}
