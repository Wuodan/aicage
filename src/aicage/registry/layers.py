from __future__ import annotations

from aicage.docker.query import get_local_rootfs_layers


def base_layer_missing(base_image_ref: str, final_image_ref: str) -> bool | None:
    base_layers = get_local_rootfs_layers(base_image_ref)
    if base_layers is None:
        return None
    final_layers = get_local_rootfs_layers(final_image_ref)
    if final_layers is None:
        return None
    return base_layers[-1] not in final_layers
