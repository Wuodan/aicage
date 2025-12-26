import tempfile
from pathlib import Path
from unittest import TestCase

from aicage.config.config_store import SettingsStore
from aicage.registry.images_metadata._cache import (
    _metadata_cache_path,
    load_cached_payload,
    save_cached_payload,
)


class ImagesMetadataCacheTests(TestCase):
    def test_save_and_load_cached_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = SettingsStore(base_dir=Path(tmp_dir), ensure_global_config=False)
            payload = "payload"
            save_cached_payload(store, payload)
            self.assertEqual(payload, load_cached_payload(store))

    def test_load_cached_payload_returns_none_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = SettingsStore(base_dir=Path(tmp_dir), ensure_global_config=False)
            self.assertIsNone(load_cached_payload(store))

    def test_metadata_cache_path_uses_store_base_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = SettingsStore(base_dir=Path(tmp_dir), ensure_global_config=False)
            cache_path = _metadata_cache_path(store)
            self.assertEqual(Path(tmp_dir) / "images-metadata.yaml", cache_path)
