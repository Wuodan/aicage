from __future__ import annotations

from logging import Logger

from aicage.config.global_config import GlobalConfig
from aicage.docker.pull import run_pull
from aicage.docker.query import get_local_repo_digest
from aicage.docker.remote_query import get_remote_repo_digest
from aicage.docker.types import ImageRefRepository, RegistryApiConfig, RemoteImageRef
from aicage.registry._logs import pull_log_path
from aicage.registry.errors import RegistryError


def ensure_version_check_image(image_ref: str, global_cfg: GlobalConfig, logger: Logger) -> None:
    local_image, remote_image = _version_check_images(image_ref, global_cfg)
    local_digest = get_local_repo_digest(local_image)
    if local_digest is None:
        _pull_version_check_image(image_ref, logger)
        return

    remote_digest = get_remote_repo_digest(remote_image)
    if remote_digest is None or remote_digest == local_digest:
        return

    _pull_version_check_image(image_ref, logger)


def _pull_version_check_image(image_ref: str, logger: Logger) -> None:
    log_path = pull_log_path(image_ref)
    try:
        run_pull(image_ref, log_path)
    except RegistryError:
        logger.warning("Version check image pull failed; using local image (logs: %s).", log_path)


def _version_check_images(
    image_ref: str, global_cfg: GlobalConfig
) -> tuple[ImageRefRepository, RemoteImageRef]:
    registry, repository = _split_image_ref(image_ref, global_cfg.image_registry)
    local_repository = f"{registry}/{repository}" if registry else repository
    local_image = ImageRefRepository(image_ref=image_ref, repository=local_repository)
    remote_image = RemoteImageRef(
        image=ImageRefRepository(image_ref=image_ref, repository=repository),
        registry_api=RegistryApiConfig(
            registry_api_url=global_cfg.image_registry_api_url,
            registry_api_token_url=global_cfg.image_registry_api_token_url,
        ),
    )
    return local_image, remote_image


def _split_image_ref(image_ref: str, default_registry: str) -> tuple[str, str]:
    name = _strip_reference(image_ref)
    parts = name.split("/", 1)
    if len(parts) == 1:
        return default_registry, name
    registry, remainder = parts
    if "." in registry or ":" in registry or registry == "localhost":
        return registry, remainder
    return default_registry, name


def _strip_reference(image_ref: str) -> str:
    if "@" in image_ref:
        return image_ref.split("@", 1)[0]
    last_colon = image_ref.rfind(":")
    if last_colon > image_ref.rfind("/"):
        return image_ref[:last_colon]
    return image_ref
