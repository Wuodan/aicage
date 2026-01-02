from __future__ import annotations

from typing import TYPE_CHECKING

from aicage._logging import get_logger
from aicage.errors import CliError
from aicage.registry import _local_query, _remote_query
from aicage.registry._logs import pull_log_path
from aicage.registry._pull_runner import run_pull

if TYPE_CHECKING:
    from aicage.config.global_config import GlobalConfig


def refresh_base_digest(
    base_image_ref: str,
    base_repository: str,
    global_cfg: GlobalConfig,
) -> str | None:
    logger = get_logger()
    local_digest = _local_query.get_local_repo_digest_for_repo(base_image_ref, base_repository)
    remote_digest = _remote_query.get_remote_repo_digest_for_repo(
        base_image_ref,
        global_cfg.image_base_repository,
        global_cfg,
    )
    if remote_digest is None or remote_digest == local_digest:
        return local_digest

    log_path = pull_log_path(base_image_ref)
    try:
        run_pull(base_image_ref, log_path)
    except CliError:
        if local_digest:
            logger.warning(
                "Base image pull failed; using local base image (logs: %s).", log_path
            )
            return local_digest
        raise

    return _local_query.get_local_repo_digest_for_repo(base_image_ref, base_repository)
