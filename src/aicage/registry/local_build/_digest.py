from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from aicage._logging import get_logger
from aicage.errors import CliError
from aicage.registry import _local_query, _remote_query

if TYPE_CHECKING:
    from aicage.config.global_config import GlobalConfig


def refresh_base_digest(
    base_image_ref: str,
    base_repository: str,
    global_cfg: GlobalConfig,
    pull_log_path: Path,
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

    pull_log_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[aicage] Pulling base image {base_image_ref} (logs: {pull_log_path})...")
    logger.info("Pulling base image %s (logs: %s)", base_image_ref, pull_log_path)
    with pull_log_path.open("w", encoding="utf-8") as log_handle:
        pull = subprocess.run(
            ["docker", "pull", base_image_ref],
            check=False,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
        )
    if pull.returncode != 0:
        message = "docker pull failed"
        if pull_log_path.is_file():
            message = f"{message}; see {pull_log_path}"
        if local_digest:
            logger.warning("Base image pull failed; using local base image: %s", message)
            return local_digest
        raise CliError(message)

    return _local_query.get_local_repo_digest_for_repo(base_image_ref, base_repository)
