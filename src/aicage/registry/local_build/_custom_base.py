from __future__ import annotations

from pathlib import Path

from aicage._logging import get_logger
from aicage.config.images_metadata.models import BaseMetadata
from aicage.docker.build import run_custom_base_build
from aicage.docker.errors import DockerError
from aicage.docker.query import local_image_exists
from aicage.registry._time import now_iso
from aicage.registry.digest.remote_digest import get_remote_digest

from ._custom_base_store import CustomBaseBuildRecord, CustomBaseBuildStore
from ._logs import custom_base_log_path


def custom_base_image_ref(base: str) -> str:
    return f"aicage-image-base:{base}"


def ensure_custom_base_image(base: str, base_metadata: BaseMetadata, base_dir: Path) -> None:
    logger = get_logger()
    image_ref = custom_base_image_ref(base)
    local_exists = local_image_exists(image_ref)
    store = CustomBaseBuildStore()
    record = store.load(base)
    remote_digest = get_remote_digest(base_metadata.from_image)

    if not _should_build(local_exists, record, base_metadata, remote_digest):
        return

    log_path = custom_base_log_path(base)
    try:
        run_custom_base_build(
            dockerfile_path=base_dir / "Dockerfile",
            build_root=base_dir,
            from_image=base_metadata.from_image,
            image_ref=image_ref,
            log_path=log_path,
        )
    except DockerError:
        if local_exists:
            logger.warning(
                "Custom base build failed; using local base image (logs: %s).", log_path
            )
            return
        raise

    store.save(
        CustomBaseBuildRecord(
            base=base,
            from_image=base_metadata.from_image,
            from_image_digest=remote_digest or "",
            image_ref=image_ref,
            built_at=now_iso(),
        )
    )


def _should_build(
    local_exists: bool,
    record: CustomBaseBuildRecord | None,
    base_metadata: BaseMetadata,
    remote_digest: str | None,
) -> bool:
    if not local_exists:
        return True
    if record is None:
        return True
    if record.from_image != base_metadata.from_image:
        return True
    if remote_digest and record.from_image_digest != remote_digest:
        return True
    return False
