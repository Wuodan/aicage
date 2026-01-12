from __future__ import annotations

from ._parser import ParsedImageRef
from ._registry import get_manifest_digest

_DOCKER_IO_REGISTRY: str = "registry-1.docker.io"


def get_docker_io_digest(parsed: ParsedImageRef) -> str | None:
    if parsed.registry != _DOCKER_IO_REGISTRY:
        return None
    return get_manifest_digest(parsed.registry, parsed.repository, parsed.reference)
