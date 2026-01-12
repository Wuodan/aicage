from __future__ import annotations

from dataclasses import dataclass

_DEFAULT_DOCKER_REGISTRY: str = "registry-1.docker.io"
_DOCKER_REGISTRY_ALIASES: set[str] = {
    "docker.io",
    "index.docker.io",
    _DEFAULT_DOCKER_REGISTRY,
}


@dataclass(frozen=True)
class ParsedImageRef:
    registry: str
    repository: str
    reference: str
    is_digest: bool

    @property
    def full_repository(self) -> str:
        return f"{self.registry}/{self.repository}"


def parse_image_ref(image_ref: str) -> ParsedImageRef:
    name, reference, is_digest = _split_reference(image_ref)
    registry, repository = _split_registry(name)
    registry, repository = _normalize_registry(registry, repository)
    return ParsedImageRef(
        registry=registry,
        repository=repository,
        reference=reference,
        is_digest=is_digest,
    )


def _split_reference(image_ref: str) -> tuple[str, str, bool]:
    if "@" in image_ref:
        name, reference = image_ref.split("@", 1)
        if not reference:
            return image_ref, "", True
        return name, reference, True

    last_colon = image_ref.rfind(":")
    if last_colon > image_ref.rfind("/"):
        name = image_ref[:last_colon]
        reference = image_ref[last_colon + 1 :]
    else:
        name = image_ref
        reference = "latest"
    return name, reference, False


def _split_registry(name: str) -> tuple[str, str]:
    parts = name.split("/", 1)
    if len(parts) == 1:
        return _DEFAULT_DOCKER_REGISTRY, name
    registry, remainder = parts
    if "." in registry or ":" in registry or registry == "localhost":
        return registry, remainder
    return _DEFAULT_DOCKER_REGISTRY, name


def _normalize_registry(registry: str, repository: str) -> tuple[str, str]:
    if registry in _DOCKER_REGISTRY_ALIASES:
        registry = _DEFAULT_DOCKER_REGISTRY
        if "/" not in repository:
            repository = f"library/{repository}"
    return registry, repository
