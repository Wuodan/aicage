import tempfile
from pathlib import Path
from unittest import TestCase

import yaml

from aicage.registry.extension_build._extended_store import (
    ExtendedBuildRecord,
    ExtendedBuildStore,
)


class ExtendedStoreTests(TestCase):
    def test_load_returns_none_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = ExtendedBuildStore(base_dir=Path(tmp_dir))
            self.assertIsNone(store.load("aicage:missing"))

    def test_load_returns_none_on_invalid_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = ExtendedBuildStore(base_dir=Path(tmp_dir))
            path = store._path("aicage:invalid")
            path.write_text("- not-a-mapping\n", encoding="utf-8")
            self.assertIsNone(store.load("aicage:invalid"))

    def test_load_filters_invalid_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = ExtendedBuildStore(base_dir=Path(tmp_dir))
            path = store._path("aicage:invalid-extensions")
            payload = {
                "agent": "codex",
                "base": "ubuntu",
                "image_ref": "aicage:invalid-extensions",
                "extensions": "not-a-list",
                "extension_hash": "hash",
                "base_image": "base",
                "built_at": "2024-01-01T00:00:00+00:00",
            }
            path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")
            record = store.load("aicage:invalid-extensions")
            self.assertIsNotNone(record)
            if record is None:
                self.fail("Expected record to be loaded.")
            self.assertEqual([], record.extensions)

    def test_save_and_load_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = ExtendedBuildStore(base_dir=Path(tmp_dir))
            record = ExtendedBuildRecord(
                agent="codex",
                base="ubuntu",
                image_ref="aicage:codex-ubuntu-extra",
                extensions=["extra"],
                extension_hash="hash",
                base_image="ghcr.io/aicage/aicage:codex-ubuntu",
                built_at="2024-01-01T00:00:00+00:00",
            )
            path = store.save(record)
            self.assertTrue(path.is_file())
            loaded = store.load(record.image_ref)
            self.assertEqual(record, loaded)
