import tempfile
from pathlib import Path
from unittest import TestCase, mock

import yaml

from aicage.config.images_metadata.models import AgentMetadata
from aicage.registry.agent_version import _command as command
from aicage.registry.agent_version.checker import AgentVersionChecker
from aicage.registry.agent_version.store import _VERSION_KEY
from aicage.registry.errors import RegistryError


class AgentVersionCheckTests(TestCase):
    def test_get_version_uses_host_success_and_persists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir) / "custom"
            agent_dir.mkdir()
            (agent_dir / "version.sh").write_text("echo 1.2.3\n", encoding="utf-8")
            store_dir = Path(tmp_dir) / "state"

            with (
                mock.patch(
                    "aicage.registry.agent_version.store.paths_module.AGENT_VERSION_CHECK_STATE_DIR",
                    store_dir,
                ),
                mock.patch(
                    "aicage.registry.agent_version.checker.run_host",
                    return_value=command._CommandResult(success=True, output="1.2.3", error=""),
                ),
            ):
                checker = AgentVersionChecker()
                result = checker.get_version(
                    "custom",
                    self._agent_metadata(),
                    definition_dir=agent_dir,
                )

            self.assertEqual("1.2.3", result)
            stored = store_dir / "custom.yaml"
            self.assertTrue(stored.is_file())
            data = yaml.safe_load(stored.read_text(encoding="utf-8"))
            self.assertEqual("1.2.3", data[_VERSION_KEY])

    def test_get_version_uses_version_check_image_and_persists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir) / "custom"
            agent_dir.mkdir()
            (agent_dir / "version.sh").write_text("echo 1.2.3\n", encoding="utf-8")
            store_dir = Path(tmp_dir) / "state"

            with (
                mock.patch(
                    "aicage.registry.agent_version.store.paths_module.AGENT_VERSION_CHECK_STATE_DIR",
                    store_dir,
                ),
                mock.patch(
                    "aicage.registry.agent_version.checker.run_host",
                    return_value=command._CommandResult(success=False, output="", error="host failed"),
                ),
                mock.patch("aicage.registry.agent_version.checker.ensure_version_check_image"),
                mock.patch(
                    "aicage.registry.agent_version.checker.run_version_check_image",
                    return_value=command._CommandResult(success=True, output="1.2.3", error=""),
                ),
            ):
                checker = AgentVersionChecker()
                result = checker.get_version(
                    "custom",
                    self._agent_metadata(),
                    definition_dir=agent_dir,
                )

            self.assertEqual("1.2.3", result)
            stored = store_dir / "custom.yaml"
            self.assertTrue(stored.is_file())
            data = yaml.safe_load(stored.read_text(encoding="utf-8"))
            self.assertEqual("1.2.3", data[_VERSION_KEY])

    def test_get_version_raises_when_version_check_image_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir) / "custom"
            agent_dir.mkdir()
            (agent_dir / "version.sh").write_text("echo 1.2.3\n", encoding="utf-8")
            store_dir = Path(tmp_dir) / "state"

            with (
                mock.patch(
                    "aicage.registry.agent_version.store.paths_module.AGENT_VERSION_CHECK_STATE_DIR",
                    store_dir,
                ),
                mock.patch(
                    "aicage.registry.agent_version.checker.run_host",
                    return_value=command._CommandResult(success=False, output="", error="host failed"),
                ),
                mock.patch("aicage.registry.agent_version.checker.ensure_version_check_image"),
                mock.patch(
                    "aicage.registry.agent_version.checker.run_version_check_image",
                    return_value=command._CommandResult(
                        success=False,
                        output="",
                        error="version check failed",
                    ),
                ),
            ):
                checker = AgentVersionChecker()
                with self.assertRaises(RegistryError) as raised:
                    checker.get_version(
                        "custom",
                        self._agent_metadata(),
                        definition_dir=agent_dir,
                    )
            self.assertIn("version check failed", str(raised.exception))

    def test_get_version_raises_on_missing_version_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir) / "custom"
            agent_dir.mkdir()
            store_dir = Path(tmp_dir) / "state"
            with mock.patch(
                "aicage.registry.agent_version.store.paths_module.AGENT_VERSION_CHECK_STATE_DIR",
                store_dir,
            ):
                checker = AgentVersionChecker()
                with self.assertRaises(RegistryError):
                    checker.get_version(
                        "custom",
                        self._agent_metadata(),
                        definition_dir=agent_dir,
                    )
            self.assertFalse((store_dir / "custom.yaml").exists())

    @staticmethod
    def _agent_metadata() -> AgentMetadata:
        return AgentMetadata(
            agent_path="~/.custom",
            agent_full_name="Custom",
            agent_homepage="https://example.com",
            build_local=True,
            valid_bases={},
            local_definition_dir=Path("/tmp/definition"),
        )
