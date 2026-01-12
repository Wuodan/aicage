from __future__ import annotations

from aicage._logging import get_logger
from aicage.docker.pull import run_pull
from aicage.docker.query import get_local_repo_digest_for_repo
from aicage.registry._logs import pull_log_path
from aicage.registry.digest.remote_digest import get_remote_digest
from aicage.registry.errors import RegistryError


def refresh_base_digest(
    base_image_ref: str,
    base_repository: str,
) -> str | None:
    logger = get_logger()
    local_digest = get_local_repo_digest_for_repo(base_image_ref, base_repository)
    remote_digest = get_remote_digest(base_image_ref)
    if remote_digest is None or remote_digest == local_digest:
        return local_digest

    log_path = pull_log_path(base_image_ref)
    try:
        run_pull(base_image_ref, log_path)
    except RegistryError:
        if local_digest:
            logger.warning(
                "Base image pull failed; using local base image (logs: %s).", log_path
            )
            return local_digest
        raise

    return get_local_repo_digest_for_repo(base_image_ref, base_repository)
