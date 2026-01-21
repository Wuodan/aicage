from pathlib import Path

from aicage.config.agent.models import AgentMetadata
from aicage.config.base.models import BaseMetadata
from aicage.config.config_store import SettingsStore
from aicage.config.context import ConfigContext
from aicage.config.project_config import AgentConfig, ProjectConfig


def build_context(
    store: SettingsStore,
    project_path: Path,
    bases: list[str],
    agents: dict[str, AgentConfig] | None = None,
) -> ConfigContext:
    base_entries, agent_entries = build_agents_and_bases(bases)
    return ConfigContext(
        store=store,
        project_cfg=ProjectConfig(path=str(project_path), agents=agents or {}),
        agents=agent_entries,
        bases=base_entries,
        extensions={},
    )


def build_agents_and_bases(
    bases: list[str],
    agent_name: str = "codex",
    build_local: bool = False,
) -> tuple[dict[str, BaseMetadata], dict[str, AgentMetadata]]:
    base_entries: dict[str, BaseMetadata] = {
        name: BaseMetadata(
            from_image="ubuntu:latest",
            base_image_distro="Ubuntu",
            base_image_description="Default",
            build_local=False,
            local_definition_dir=Path(f"/tmp/{name}"),
        )
        for name in bases
    }
    agents = {
        agent_name: AgentMetadata(
            agent_path=["~/.codex"],
            agent_full_name="Codex CLI",
            agent_homepage="https://example.com",
            build_local=build_local,
            valid_bases={
                name: f"ghcr.io/aicage/aicage:{agent_name}-{name}" for name in bases
            },
            local_definition_dir=Path(f"/tmp/{agent_name}"),
        )
    }
    return base_entries, agents
