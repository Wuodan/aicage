from __future__ import annotations


def local_image_ref(local_image_repository: str, agent: str, base: str) -> str:
    tag = f"{agent}-{base}".lower().replace("/", "-")
    return f"{local_image_repository}:{tag}"
