from __future__ import annotations

from aicage.constants import IMAGE_REGISTRY, IMAGE_REPOSITORY
from aicage.docker.query import get_local_repo_digest
from aicage.docker.types import ImageRefRepository
from aicage.registry.digest.remote_digest import get_remote_digest


def decide_pull(image_ref: str) -> bool:
    # Local digests include registry prefix; registry API uses repository only.
    local_repository = f"{IMAGE_REGISTRY}/{IMAGE_REPOSITORY}"
    local_digest = get_local_repo_digest(
        ImageRefRepository(
            image_ref=image_ref,
            repository=local_repository,
        )
    )
    if local_digest is None:
        return True

    remote_digest = get_remote_digest(image_ref)
    if remote_digest is None:
        return False

    return local_digest != remote_digest
