from __future__ import annotations

IMAGE_REGISTRY: str = "ghcr.io"
_IMAGE_REGISTRY_API_URL: str = "https://ghcr.io/v2"
_IMAGE_REGISTRY_API_TOKEN_URL: str = (
    "https://ghcr.io/token?service=ghcr.io&scope=repository"
)
IMAGE_REPOSITORY: str = "aicage/aicage"
IMAGE_BASE_REPOSITORY: str = "aicage/aicage-image-base"
DEFAULT_IMAGE_BASE: str = "ubuntu"
VERSION_CHECK_IMAGE: str = "ghcr.io/aicage/aicage-image-util:agent-version"
LOCAL_IMAGE_REPOSITORY: str = "aicage"

DEFAULT_EXTENDED_IMAGE_NAME: str = "aicage-extended"
