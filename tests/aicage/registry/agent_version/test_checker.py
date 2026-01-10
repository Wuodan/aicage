import io
import tempfile
from pathlib import Path
from subprocess import CompletedProcess
from unittest import TestCase, mock

import yaml
from docker.errors import ContainerError
from docker.models.containers import Container

from aicage.config.global_config import GlobalConfig
from aicage.errors import CliError
from aicage.registry.agent_version import AgentVersionChecker, VersionCheckStore
from aicage.registry.agent_version import checker as version_checker
from aicage.registry.agent_version.store import _VERSION_KEY
from aicage.registry.images_metadata.models import AgentMetadata


class AgentVersionCheckTests(TestCase):
    def test_check_uses_host_success_and_persists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir) / "custom"
            agent_dir.mkdir()
            (agent_dir / "version.sh").write_text("echo 1.2.3\n", encoding="utf-8")
            store_dir = Path(tmp_dir) / "state"
            checker = AgentVersionChecker(
                global_cfg=self._global_config(),
                store=VersionCheckStore(store_dir),
            )

            with (
                mock.patch(
                    "aicage.registry.agent_version.checker.subprocess.run",
                    return_value=CompletedProcess([], 0, stdout="1.2.3\n", stderr=""),
                ),
                mock.patch("sys.stderr", new_callable=io.StringIO),
            ):
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

    def test_check_uses_builder_fallback_and_persists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir) / "custom"
            agent_dir.mkdir()
            (agent_dir / "version.sh").write_text("echo 1.2.3\n", encoding="utf-8")
            store_dir = Path(tmp_dir) / "state"
            checker = AgentVersionChecker(
                global_cfg=self._global_config(),
                store=VersionCheckStore(store_dir),
            )

            with (
                mock.patch(
                    "aicage.registry.agent_version.checker.subprocess.run",
                    return_value=CompletedProcess([], 1, stdout="", stderr="host failed"),
                ),
                mock.patch("aicage.registry.agent_version.checker._ensure_version_check_image"),
                mock.patch("aicage.docker.run.get_docker_client") as client_mock,
                mock.patch("sys.stderr", new_callable=io.StringIO),
            ):
                client = client_mock.return_value
                client.containers.run.return_value = "1.2.3\n"
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

    def test_check_raises_when_builder_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir) / "custom"
            agent_dir.mkdir()
            (agent_dir / "version.sh").write_text("echo 1.2.3\n", encoding="utf-8")
            store_dir = Path(tmp_dir) / "state"
            checker = AgentVersionChecker(
                global_cfg=self._global_config(),
                store=VersionCheckStore(store_dir),
            )

            with (
                mock.patch(
                    "aicage.registry.agent_version.checker.subprocess.run",
                    return_value=CompletedProcess([], 1, stdout="", stderr="host failed"),
                ),
                mock.patch("aicage.registry.agent_version.checker._ensure_version_check_image"),
                mock.patch("aicage.docker.run.get_docker_client") as client_mock,
                mock.patch("sys.stderr", new_callable=io.StringIO),
            ):
                client = client_mock.return_value
                client.containers.run.side_effect = ContainerError(
                    container=mock.Mock(spec=Container),
                    exit_status=1,
                    command=["/bin/bash", "/agent/version.sh"],
                    image="ghcr.io/aicage/aicage-image-util:agent-version",
                    stderr="builder failed",
                )
                with self.assertRaises(CliError) as raised:
                    checker.get_version(
                        "custom",
                        self._agent_metadata(),
                        definition_dir=agent_dir,
                    )
            self.assertIn("builder failed", str(raised.exception))

    def test_check_raises_on_missing_version_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir) / "custom"
            agent_dir.mkdir()
            store_dir = Path(tmp_dir) / "state"
            checker = AgentVersionChecker(
                global_cfg=self._global_config(),
                store=VersionCheckStore(store_dir),
            )
            with self.assertRaises(CliError):
                checker.get_version(
                    "custom",
                    self._agent_metadata(),
                    definition_dir=agent_dir,
                )
            self.assertFalse((store_dir / "custom.yaml").exists())

    def test_version_check_pulls_when_local_missing(self) -> None:
        global_cfg = self._global_config()
        image_ref = global_cfg.version_check_image
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry.agent_version.checker.get_local_repo_digest",
                    return_value=None,
                ) as local_mock,
                mock.patch("aicage.registry.agent_version.checker.get_remote_repo_digest") as remote_mock,
                mock.patch("aicage.registry.agent_version.checker.run_pull") as pull_mock,
                mock.patch(
                    "aicage.registry.agent_version.checker.pull_log_path",
                    return_value=log_path,
                ),
            ):
                version_checker._ensure_version_check_image(
                    image_ref=image_ref,
                    global_cfg=global_cfg,
                    logger=mock.Mock(),
                )
        local_mock.assert_called_once()
        remote_mock.assert_not_called()
        pull_mock.assert_called_once_with(image_ref, log_path)

    def test_version_check_skips_pull_when_remote_unknown(self) -> None:
        global_cfg = self._global_config()
        image_ref = global_cfg.version_check_image
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry.agent_version.checker.get_local_repo_digest",
                    return_value="sha256:local",
                ),
                mock.patch(
                    "aicage.registry.agent_version.checker.get_remote_repo_digest",
                    return_value=None,
                ) as remote_mock,
                mock.patch("aicage.registry.agent_version.checker.run_pull") as pull_mock,
                mock.patch(
                    "aicage.registry.agent_version.checker.pull_log_path",
                    return_value=log_path,
                ),
            ):
                version_checker._ensure_version_check_image(
                    image_ref=image_ref,
                    global_cfg=global_cfg,
                    logger=mock.Mock(),
                )
        remote_mock.assert_called_once()
        pull_mock.assert_not_called()

    @staticmethod
    def _global_config() -> GlobalConfig:
        return GlobalConfig(
            image_registry="ghcr.io",
            image_registry_api_url="https://ghcr.io/v2",
            image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
            image_repository="aicage/aicage",
            image_base_repository="aicage/aicage-image-base",
            default_image_base="ubuntu",
            version_check_image="ghcr.io/aicage/aicage-image-util:agent-version",
            local_image_repository="aicage",
            agents={},
        )

    @staticmethod
    def _agent_metadata() -> AgentMetadata:
        return AgentMetadata(
            agent_path="~/.custom",
            agent_full_name="Custom",
            agent_homepage="https://example.com",
            valid_bases={},
            local_definition_dir=Path("/tmp/definition"),
        )
