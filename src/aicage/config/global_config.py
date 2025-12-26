from dataclasses import dataclass, field
from typing import Any

from .errors import ConfigError

__all__ = ["GlobalConfig"]


@dataclass
class GlobalConfig:
    image_registry: str
    image_registry_api_url: str
    image_registry_api_token_url: str
    image_repository: str
    default_image_base: str
    images_metadata_release_api_url: str
    images_metadata_asset_name: str
    images_metadata_download_retries: int
    images_metadata_retry_backoff_seconds: float
    tools: dict[str, dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "GlobalConfig":
        required = (
            "image_registry",
            "image_registry_api_url",
            "image_registry_api_token_url",
            "image_repository",
            "default_image_base",
            "images_metadata_release_api_url",
            "images_metadata_asset_name",
            "images_metadata_download_retries",
            "images_metadata_retry_backoff_seconds",
        )
        missing = [key for key in required if key not in data]
        if missing:
            raise ConfigError(f"Missing required config values: {', '.join(missing)}.")
        return cls(
            image_registry=data["image_registry"],
            image_registry_api_url=data["image_registry_api_url"],
            image_registry_api_token_url=data["image_registry_api_token_url"],
            image_repository=data["image_repository"],
            default_image_base=data["default_image_base"],
            images_metadata_release_api_url=data["images_metadata_release_api_url"],
            images_metadata_asset_name=data["images_metadata_asset_name"],
            images_metadata_download_retries=int(data["images_metadata_download_retries"]),
            images_metadata_retry_backoff_seconds=float(
                data["images_metadata_retry_backoff_seconds"]
            ),
            tools=data.get("tools", {}) or {},
        )

    def to_mapping(self) -> dict[str, Any]:
        return {
            "image_registry": self.image_registry,
            "image_registry_api_url": self.image_registry_api_url,
            "image_registry_api_token_url": self.image_registry_api_token_url,
            "image_repository": self.image_repository,
            "default_image_base": self.default_image_base,
            "images_metadata_release_api_url": self.images_metadata_release_api_url,
            "images_metadata_asset_name": self.images_metadata_asset_name,
            "images_metadata_download_retries": self.images_metadata_download_retries,
            "images_metadata_retry_backoff_seconds": self.images_metadata_retry_backoff_seconds,
            "tools": self.tools,
        }
