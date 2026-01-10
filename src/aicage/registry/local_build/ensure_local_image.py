from __future__ import annotations

from pathlib import Path

from aicage.config.runtime_config import RunConfig
from aicage.docker.build import run_build
from aicage.errors import CliError
from aicage.registry.agent_version import AgentVersionChecker
from aicage.registry.images_metadata.models import AgentMetadata

from ._digest import refresh_base_digest
from ._logs import build_log_path
from ._plan import base_image_ref, base_repository, now_iso, should_build
from ._store import BuildRecord, BuildStore


def ensure_local_image(run_config: RunConfig) -> None:
    agent_metadata = run_config.images_metadata.agents[run_config.agent]
    definition_dir = agent_metadata.local_definition_dir
    if definition_dir is None:
        raise CliError(f"Missing local definition for '{run_config.agent}'.")

    base_image = base_image_ref(run_config)
    base_repo = base_repository(run_config)
    refresh_base_digest(
        base_image_ref=base_image,
        base_repository=base_repo,
        global_cfg=run_config.global_cfg,
    )

    store = BuildStore()
    record = store.load(run_config.agent, run_config.base)

    agent_version = _get_agent_version(run_config, agent_metadata, definition_dir)
    needs_build = should_build(
        run_config=run_config,
        record=record,
        base_image_ref=base_image,
        agent_version=agent_version,
    )
    if not needs_build:
        return

    log_path = build_log_path(run_config.agent, run_config.base)
    run_build(
        run_config=run_config,
        base_image_ref=base_image,
        log_path=log_path,
    )

    store.save(
        BuildRecord(
            agent=run_config.agent,
            base=run_config.base,
            agent_version=agent_version,
            base_image=base_image,
            image_ref=run_config.image_ref,
            built_at=now_iso(),
        )
    )


def _get_agent_version(
    run_config: RunConfig,
    agent_metadata: AgentMetadata,
    definition_dir: Path,
) -> str:
    checker = AgentVersionChecker(run_config.global_cfg)
    return checker.get_version(
        run_config.agent,
        agent_metadata,
        definition_dir,
    )
