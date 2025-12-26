from __future__ import annotations

from pathlib import Path

from aicage.config.config_store import SettingsStore


def _metadata_cache_path(store: SettingsStore) -> Path:
    return store.base_dir / "images-metadata.yaml"


def load_cached_payload(store: SettingsStore) -> str | None:
    path = _metadata_cache_path(store)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def save_cached_payload(store: SettingsStore, payload: str) -> None:
    path = _metadata_cache_path(store)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")
