from __future__ import annotations

from logging import Logger

from aicage.constants import IMAGE_REGISTRY
from aicage.docker.pull import run_pull
from aicage.docker.query import get_local_repo_digest_for_repo
from aicage.registry._logs import pull_log_path
from aicage.registry.digest.remote_digest import get_remote_digest
from aicage.registry.errors import RegistryError


def ensure_version_check_image(image_ref: str, logger: Logger) -> None:
    local_digest = get_local_repo_digest_for_repo(
        image_ref,
        _local_repository(image_ref, IMAGE_REGISTRY),
    )
    if local_digest is None:
        _pull_version_check_image(image_ref, logger)
        return

    remote_digest = get_remote_digest(image_ref)
    if remote_digest is None or remote_digest == local_digest:
        return

    _pull_version_check_image(image_ref, logger)


def _pull_version_check_image(image_ref: str, logger: Logger) -> None:
    log_path = pull_log_path(image_ref)
    try:
        run_pull(image_ref, log_path)
    except RegistryError:
        logger.warning("Version check image pull failed; using local image (logs: %s).", log_path)


def _local_repository(image_ref: str, default_registry: str) -> str:
    name = _strip_reference(image_ref)
    parts = name.split("/", 1)
    if len(parts) == 1:
        return f"{default_registry}/{name}"
    registry, remainder = parts
    if "." in registry or ":" in registry or registry == "localhost":
        return f"{registry}/{remainder}"
    return f"{default_registry}/{name}"


def _strip_reference(image_ref: str) -> str:
    if "@" in image_ref:
        return image_ref.split("@", 1)[0]
    last_colon = image_ref.rfind(":")
    if last_colon > image_ref.rfind("/"):
        return image_ref[:last_colon]
    return image_ref
