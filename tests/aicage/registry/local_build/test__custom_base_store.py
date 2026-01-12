import tempfile
from pathlib import Path
from unittest import TestCase

from aicage.registry.local_build._custom_base_store import (
    CustomBaseBuildRecord,
    CustomBaseBuildStore,
)


class CustomBaseBuildStoreTests(TestCase):
    def test_load_returns_none_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = CustomBaseBuildStore(Path(tmp_dir))
            self.assertIsNone(store.load("missing"))

    def test_save_persists_record(self) -> None:
        record = CustomBaseBuildRecord(
            base="custom",
            from_image="ubuntu:latest",
            from_image_digest="sha256:deadbeef",
            image_ref="aicage-image-base:custom",
            built_at="2024-01-01T00:00:00+00:00",
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            store = CustomBaseBuildStore(base_dir)

            path = store.save(record)
            loaded = store.load("custom")

            self.assertTrue(path.is_file())
            self.assertEqual(record, loaded)
