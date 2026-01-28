import subprocess

from docker.errors import DockerException, ImageNotFound

from aicage._logging import get_logger

from ._client import get_docker_client
from .types import ImageRefRepository


def local_image_exists(image_ref: str) -> bool:
    client = get_docker_client()
    try:
        client.images.get(image_ref)
    except ImageNotFound:
        return False
    return True


def get_local_repo_digest(image: ImageRefRepository) -> str | None:
    return get_local_repo_digest_for_repo(image.image_ref, image.repository)


def get_local_repo_digest_for_repo(image_ref: str, repository: str) -> str | None:
    try:
        client = get_docker_client()
        image = client.images.get(image_ref)
    except (ImageNotFound, DockerException):
        return None

    repo_digests = image.attrs.get("RepoDigests")
    if not isinstance(repo_digests, list):
        return None

    for entry in repo_digests:
        if not isinstance(entry, str):
            continue
        repo, sep, digest = entry.partition("@")
        if sep and repo == repository and digest:
            return digest

    return None


def get_local_rootfs_layers(image_ref: str) -> list[str] | None:
    try:
        client = get_docker_client()
        image = client.images.get(image_ref)
    except (ImageNotFound, DockerException):
        return None

    rootfs = image.attrs.get("RootFS")
    if not isinstance(rootfs, dict):
        return None
    layers = rootfs.get("Layers")
    if not isinstance(layers, list):
        return None
    filtered = [layer for layer in layers if isinstance(layer, str)]
    if not filtered:
        return None
    return filtered


def _remove_old_image_digest(repository: str, old_digest: str) -> None:
    image_ref = f"{repository}@{old_digest}"
    logger = get_logger()
    result = subprocess.run(
        ["docker", "image", "rm", image_ref],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        logger.warning("Failed to remove old image digest %s", image_ref)
        return
    logger.info("Removed old image digest %s", image_ref)


def cleanup_old_digest(
    repository: str,
    local_digest: str | None,
    image_ref: str,
) -> None:
    if local_digest is None:
        return
    updated_digest = get_local_repo_digest_for_repo(image_ref, repository)
    if updated_digest is None or updated_digest == local_digest:
        return
    _remove_old_image_digest(repository, local_digest)
