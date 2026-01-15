from dataclasses import dataclass
from pathlib import Path

from aicage.cli_types import ParsedArgs
from aicage.config._file_locking import lock_project_config
from aicage.config.agent.loader import load_agents
from aicage.config.base.loader import load_bases
from aicage.config.config_store import SettingsStore
from aicage.config.context import ConfigContext
from aicage.config.extensions.loader import load_extensions
from aicage.config.project_config import AgentConfig
from aicage.registry.image_selection.models import ImageSelection
from aicage.registry.image_selection.selection import select_agent_image
from aicage.runtime.mounts.resolver import resolve_mounts
from aicage.runtime.prompts.confirm import prompt_persist_docker_args
from aicage.runtime.run_args import MountSpec


@dataclass(frozen=True)
class RunConfig:
    project_path: Path
    agent: str
    context: ConfigContext
    selection: ImageSelection
    project_docker_args: str
    mounts: list[MountSpec]


def load_run_config(agent: str, parsed: ParsedArgs | None = None) -> RunConfig:
    store = SettingsStore()
    project_path = Path.cwd().resolve()
    project_config_path = store.project_config_path(project_path)

    with lock_project_config(project_config_path):
        bases = load_bases()
        agents = load_agents(bases)
        project_cfg = store.load_project(project_path)
        context = ConfigContext(
            store=store,
            project_cfg=project_cfg,
            agents=agents,
            bases=bases,
            extensions=load_extensions(),
        )
        selection = select_agent_image(agent, context)
        agent_cfg = project_cfg.agents.setdefault(agent, AgentConfig())

        existing_project_docker_args: str = agent_cfg.docker_args
        if agent_cfg.base is None:
            agent_cfg.base = selection.base

        mounts = resolve_mounts(context, agent, parsed)

        _persist_docker_args(agent_cfg, parsed)
        store.save_project(project_path, project_cfg)

        return RunConfig(
            project_path=project_path,
            agent=agent,
            context=context,
            selection=selection,
            project_docker_args=existing_project_docker_args,
            mounts=mounts,
        )


def _persist_docker_args(agent_cfg: AgentConfig, parsed: ParsedArgs | None) -> None:
    if parsed is None or not parsed.docker_args:
        return
    existing = agent_cfg.docker_args
    if existing == parsed.docker_args:
        return

    if prompt_persist_docker_args(parsed.docker_args, existing):
        agent_cfg.docker_args = parsed.docker_args
