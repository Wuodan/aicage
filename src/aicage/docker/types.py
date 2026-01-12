from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImageRefRepository:
    image_ref: str
    repository: str


@dataclass(frozen=True)
class RegistryApiConfig:
    registry_api_url: str
    registry_api_token_url: str

