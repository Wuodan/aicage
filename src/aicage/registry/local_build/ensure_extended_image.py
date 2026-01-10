from __future__ import annotations

from aicage.config.runtime_config import RunConfig
from aicage.docker.build import run_extended_build
from aicage.errors import CliError
from aicage.registry._hashing import new_hasher
from aicage.registry.extensions import ExtensionMetadata, extension_hash, load_extensions
from aicage.registry.image_pull import pull_image
from aicage.registry.local_build.ensure_local_image import ensure_local_image

from ._extended_plan import should_build_extended
from ._extended_store import ExtendedBuildRecord, ExtendedBuildStore
from ._logs import build_log_path_for_image
from ._plan import now_iso


def ensure_extended_image(run_config: RunConfig) -> None:
    if not run_config.extensions:
        raise CliError("No extensions selected for extended image build.")

    extensions = load_extensions()
    resolved = _resolve_extensions(run_config.extensions, extensions)
    base_run_config = _base_run_config(run_config)

    agent_metadata = run_config.images_metadata.agents[run_config.agent]
    if agent_metadata.local_definition_dir is None:
        pull_image(base_run_config)
    else:
        ensure_local_image(base_run_config)

    combined_hash = _combined_extension_hash(resolved)
    store = ExtendedBuildStore()
    record = store.load(run_config.image_ref)
    needs_build = should_build_extended(
        run_config=run_config,
        record=record,
        base_image_ref=run_config.base_image_ref,
        extension_hash=combined_hash,
    )
    if not needs_build:
        return

    log_path = build_log_path_for_image(run_config.image_ref)
    run_extended_build(
        run_config=run_config,
        base_image_ref=run_config.base_image_ref,
        extensions=resolved,
        log_path=log_path,
    )
    store.save(
        ExtendedBuildRecord(
            agent=run_config.agent,
            base=run_config.base,
            image_ref=run_config.image_ref,
            extensions=list(run_config.extensions),
            extension_hash=combined_hash,
            base_image=run_config.base_image_ref,
            built_at=now_iso(),
        )
    )


def _resolve_extensions(
    extension_ids: list[str],
    extensions: dict[str, ExtensionMetadata],
) -> list[ExtensionMetadata]:
    missing = [ext for ext in extension_ids if ext not in extensions]
    if missing:
        raise CliError(f"Missing extensions: {', '.join(sorted(missing))}.")
    return [extensions[ext] for ext in extension_ids]


def _combined_extension_hash(extensions: list[ExtensionMetadata]) -> str:
    digest = new_hasher()
    for extension in extensions:
        digest.update(extension.extension_id.encode("utf-8"))
        digest.update(extension_hash(extension).encode("utf-8"))
    return digest.hexdigest()


def _base_run_config(run_config: RunConfig) -> RunConfig:
    return RunConfig(
        project_path=run_config.project_path,
        agent=run_config.agent,
        base=run_config.base,
        image_ref=run_config.base_image_ref,
        base_image_ref=run_config.base_image_ref,
        extensions=[],
        global_cfg=run_config.global_cfg,
        images_metadata=run_config.images_metadata,
        project_docker_args=run_config.project_docker_args,
        mounts=run_config.mounts,
    )
