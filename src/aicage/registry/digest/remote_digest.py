from __future__ import annotations

from ._docker_io import get_docker_io_digest
from ._ghcr import get_ghcr_digest
from ._parser import parse_image_ref


def get_remote_digest(image_ref: str) -> str | None:
    parsed = parse_image_ref(image_ref)
    if parsed.is_digest:
        return parsed.reference
    digest = get_ghcr_digest(parsed)
    if digest:
        return digest
    return get_docker_io_digest(parsed)
