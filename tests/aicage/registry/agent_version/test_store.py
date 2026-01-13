import tempfile
from pathlib import Path
from unittest import TestCase, mock

import yaml

from aicage.registry.agent_version.store import (
    _AGENT_KEY,
    _CHECKED_AT_KEY,
    _VERSION_KEY,
    VersionCheckStore,
)


class VersionCheckStoreTests(TestCase):
    def test_save_writes_sanitized_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            with mock.patch(
                "aicage.registry.agent_version.store.paths_module.AGENT_VERSION_CHECK_STATE_DIR",
                base_dir,
            ):
                store = VersionCheckStore()

                path = store.save("custom/agent", "1.2.3")

                self.assertEqual(base_dir / "custom_agent.yaml", path)
                payload = yaml.safe_load(path.read_text(encoding="utf-8"))
                self.assertEqual("custom/agent", payload[_AGENT_KEY])
                self.assertEqual("1.2.3", payload[_VERSION_KEY])
                self.assertIn(_CHECKED_AT_KEY, payload)
