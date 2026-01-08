from __future__ import annotations

from docker.errors import DockerException, ImageNotFound

from aicage.docker_client import get_docker_client


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
