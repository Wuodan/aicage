from __future__ import annotations

from pathlib import Path

from aicage.config.images_metadata.models import AgentMetadata
from aicage.config.runtime_config import RunConfig
from aicage.docker.build import run_build
from aicage.paths import CUSTOM_BASES_DIR
from aicage.registry._time import now_iso
from aicage.registry.agent_version import AgentVersionChecker
from aicage.registry.errors import RegistryError

from ._custom_base import ensure_custom_base_image
from ._digest import refresh_base_digest
from ._logs import build_log_path
from ._plan import should_build
from ._refs import base_repository, get_base_image_ref
from ._store import BuildRecord, BuildStore


def ensure_local_image(run_config: RunConfig) -> None:
    agent_metadata = run_config.context.images_metadata.agents[run_config.agent]
    definition_dir = agent_metadata.local_definition_dir
    if definition_dir is None:
        raise RegistryError(f"Missing local definition for '{run_config.agent}'.")

    custom_base = run_config.context.custom_bases.get(run_config.selection.base)
    base_image = get_base_image_ref(run_config)
    image_ref = run_config.selection.base_image_ref
    if custom_base is not None:
        base_dir = CUSTOM_BASES_DIR / run_config.selection.base
        ensure_custom_base_image(run_config.selection.base, custom_base, base_dir)
    else:
        base_repo = base_repository(run_config)
        refresh_base_digest(
            base_image_ref=base_image,
            base_repository=base_repo,
        )

    store = BuildStore()
    record = store.load(run_config.agent, run_config.selection.base)

    agent_version = _get_agent_version(run_config, agent_metadata, definition_dir)
    needs_build = should_build(
        run_config=run_config,
        record=record,
        agent_version=agent_version,
    )
    if not needs_build:
        return

    log_path = build_log_path(run_config.agent, run_config.selection.base)
    run_build(
        run_config=run_config,
        base_image_ref=base_image,
        image_ref=image_ref,
        log_path=log_path,
    )

    store.save(
        BuildRecord(
            agent=run_config.agent,
            base=run_config.selection.base,
            agent_version=agent_version,
            base_image=base_image,
            image_ref=image_ref,
            built_at=now_iso(),
        )
    )


def _get_agent_version(
    run_config: RunConfig,
    agent_metadata: AgentMetadata,
    definition_dir: Path,
) -> str:
    checker = AgentVersionChecker()
    return checker.get_version(
        run_config.agent,
        agent_metadata,
        definition_dir,
    )
