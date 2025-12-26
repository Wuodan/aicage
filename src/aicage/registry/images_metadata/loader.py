from __future__ import annotations

import time

from aicage.config.config_store import SettingsStore
from aicage.config.global_config import GlobalConfig
from aicage.errors import CliError

from ._cache import load_cached_payload, save_cached_payload
from ._download import download_images_metadata
from .models import ImagesMetadata

__all__ = ["load_images_metadata"]


def load_images_metadata(global_cfg: GlobalConfig, store: SettingsStore) -> ImagesMetadata:
    payload, download_error = _download_with_retries(global_cfg)
    if payload is not None:
        try:
            metadata = ImagesMetadata.from_yaml(payload)
        except CliError as exc:
            download_error = str(exc)
        else:
            save_cached_payload(store, payload)
            return metadata

    cached_payload = load_cached_payload(store)
    if cached_payload is not None:
        return ImagesMetadata.from_yaml(cached_payload)

    if download_error:
        raise CliError(f"Failed to load images metadata: {download_error}")
    raise CliError("Failed to load images metadata and no cache is available.")


def _download_with_retries(global_cfg: GlobalConfig) -> tuple[str | None, str | None]:
    attempts = max(1, global_cfg.images_metadata_download_retries)
    last_error: str | None = None
    for attempt in range(1, attempts + 1):
        try:
            payload = download_images_metadata(global_cfg)
            return payload, None
        except CliError as exc:
            last_error = str(exc)
            if attempt < attempts:
                time.sleep(global_cfg.images_metadata_retry_backoff_seconds)
    return None, last_error
