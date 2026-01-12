from __future__ import annotations

from ._parser import ParsedImageRef
from ._registry import get_manifest_digest

_GHCR_REGISTRY: str = "ghcr.io"


def get_ghcr_digest(parsed: ParsedImageRef) -> str | None:
    if parsed.registry != _GHCR_REGISTRY:
        return None
    return get_manifest_digest(parsed.registry, parsed.repository, parsed.reference)
