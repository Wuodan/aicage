import tempfile
from dataclasses import replace
from pathlib import Path
from unittest import TestCase, mock

import yaml

from aicage.config.global_config import GlobalConfig
from aicage.config.runtime_config import RunConfig
from aicage.errors import CliError
from aicage.registry import _local_build
from aicage.registry._local_build import ensure_local_image
from aicage.registry.images_metadata.models import ImagesMetadata


class LocalBuildTests(TestCase):
    def test_builds_when_missing_image(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_dir = Path(tmp_dir) / "state"
            log_dir = Path(tmp_dir) / "logs"
            run_config = self._run_config()

            with (
                mock.patch("aicage.registry._local_build._DEFAULT_STATE_DIR", str(state_dir)),
                mock.patch("aicage.registry._local_build._DEFAULT_LOG_DIR", str(log_dir)),
                mock.patch("aicage.registry._local_build._local_image_exists", return_value=False),
                mock.patch("aicage.registry._local_build._refresh_base_digest", return_value="sha256:base"),
                mock.patch("aicage.registry._local_build._run_build") as build_mock,
                mock.patch(
                    "aicage.registry._local_build._local_query.get_local_repo_digest_for_repo",
                    return_value="sha256:base",
                ),
            ):
                ensure_local_image(run_config)

            build_mock.assert_called_once()
            record_path = state_dir / "claude-ubuntu.yaml"
            self.assertTrue(record_path.is_file())
            payload = yaml.safe_load(record_path.read_text(encoding="utf-8"))
            self.assertEqual("1.2.3", payload["agent_version"])

    def test_skips_when_up_to_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_dir = Path(tmp_dir) / "state"
            log_dir = Path(tmp_dir) / "logs"
            run_config = self._run_config()
            record_path = state_dir / "claude-ubuntu.yaml"
            record_path.parent.mkdir(parents=True, exist_ok=True)
            record_path.write_text(
                yaml.safe_dump(
                    {
                        "agent": "claude",
                        "base": "ubuntu",
                        "agent_version": "1.2.3",
                        "base_image": "ghcr.io/aicage/aicage-image-base:ubuntu",
                        "base_digest": "sha256:base",
                        "image_ref": "aicage:claude-ubuntu",
                        "built_at": "2024-01-01T00:00:00+00:00",
                    }
                ),
                encoding="utf-8",
            )

            with (
                mock.patch("aicage.registry._local_build._DEFAULT_STATE_DIR", str(state_dir)),
                mock.patch("aicage.registry._local_build._DEFAULT_LOG_DIR", str(log_dir)),
                mock.patch("aicage.registry._local_build._local_image_exists", return_value=True),
                mock.patch("aicage.registry._local_build._refresh_base_digest", return_value="sha256:base"),
                mock.patch("aicage.registry._local_build._run_build") as build_mock,
            ):
                ensure_local_image(run_config)

            build_mock.assert_not_called()

    def test_raises_when_missing_agent_version(self) -> None:
        run_config = RunConfig(
            project_path=Path("/tmp/project"),
            agent="claude",
            base="ubuntu",
            image_ref="aicage:claude-ubuntu",
            agent_version=None,
            global_cfg=self._run_config().global_cfg,
            images_metadata=self._images_metadata(),
            project_docker_args="",
            mounts=[],
        )
        with (
            mock.patch("aicage.registry._local_build._refresh_base_digest") as refresh_mock,
            mock.patch("aicage.registry._local_build._local_image_exists") as exists_mock,
        ):
            with self.assertRaises(CliError):
                ensure_local_image(run_config)
        refresh_mock.assert_not_called()
        exists_mock.assert_not_called()

    def test_skips_for_redistributable_agent(self) -> None:
        run_config = self._run_config()
        images_metadata = self._images_metadata()
        images_metadata.agents["claude"] = replace(
            images_metadata.agents["claude"], redistributable=True
        )
        run_config = RunConfig(
            project_path=run_config.project_path,
            agent=run_config.agent,
            base=run_config.base,
            image_ref=run_config.image_ref,
            agent_version=run_config.agent_version,
            global_cfg=run_config.global_cfg,
            images_metadata=images_metadata,
            project_docker_args=run_config.project_docker_args,
            mounts=run_config.mounts,
        )
        with mock.patch("aicage.registry._local_build._refresh_base_digest") as refresh_mock:
            ensure_local_image(run_config)
        refresh_mock.assert_not_called()

    def test_refresh_base_digest_skips_pull_when_remote_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            global_cfg = self._run_config().global_cfg
            with (
                mock.patch(
                    "aicage.registry._local_build._local_query.get_local_repo_digest_for_repo",
                    return_value="sha256:local",
                ),
                mock.patch(
                    "aicage.registry._local_build._remote_query.get_remote_repo_digest_for_repo",
                    return_value=None,
                ),
                mock.patch("aicage.registry._local_build.subprocess.run") as run_mock,
            ):
                digest = _local_build._refresh_base_digest(
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    base_repository="ghcr.io/aicage/aicage-image-base",
                    global_cfg=global_cfg,
                    pull_log_path=log_path,
                )
        self.assertEqual("sha256:local", digest)
        run_mock.assert_not_called()

    def test_refresh_base_digest_pull_failure_uses_local_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            global_cfg = self._run_config().global_cfg
            with (
                mock.patch(
                    "aicage.registry._local_build._local_query.get_local_repo_digest_for_repo",
                    return_value="sha256:local",
                ),
                mock.patch(
                    "aicage.registry._local_build._remote_query.get_remote_repo_digest_for_repo",
                    return_value="sha256:remote",
                ),
                mock.patch(
                    "aicage.registry._local_build.subprocess.run",
                    return_value=mock.Mock(returncode=1),
                ),
            ):
                digest = _local_build._refresh_base_digest(
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    base_repository="ghcr.io/aicage/aicage-image-base",
                    global_cfg=global_cfg,
                    pull_log_path=log_path,
                )
            self.assertEqual("sha256:local", digest)
            self.assertTrue(log_path.is_file())

    def test_refresh_base_digest_pull_success_updates_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            global_cfg = self._run_config().global_cfg
            with (
                mock.patch(
                    "aicage.registry._local_build._local_query.get_local_repo_digest_for_repo",
                    side_effect=["sha256:old", "sha256:new"],
                ),
                mock.patch(
                    "aicage.registry._local_build._remote_query.get_remote_repo_digest_for_repo",
                    return_value="sha256:remote",
                ),
                mock.patch(
                    "aicage.registry._local_build.subprocess.run",
                    return_value=mock.Mock(returncode=0),
                ),
            ):
                digest = _local_build._refresh_base_digest(
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    base_repository="ghcr.io/aicage/aicage-image-base",
                    global_cfg=global_cfg,
                    pull_log_path=log_path,
                )
            self.assertEqual("sha256:new", digest)
            self.assertTrue(log_path.is_file())

    def test_refresh_base_digest_pull_failure_without_local_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            global_cfg = self._run_config().global_cfg
            with (
                mock.patch(
                    "aicage.registry._local_build._local_query.get_local_repo_digest_for_repo",
                    return_value=None,
                ),
                mock.patch(
                    "aicage.registry._local_build._remote_query.get_remote_repo_digest_for_repo",
                    return_value="sha256:remote",
                ),
                mock.patch(
                    "aicage.registry._local_build.subprocess.run",
                    return_value=mock.Mock(returncode=1),
                ),
            ):
                with self.assertRaises(CliError) as exc:
                    _local_build._refresh_base_digest(
                        base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                        base_repository="ghcr.io/aicage/aicage-image-base",
                        global_cfg=global_cfg,
                        pull_log_path=log_path,
                    )
            self.assertIn("see", str(exc.exception))
            self.assertTrue(log_path.is_file())

    def test_run_build_raises_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            run_config = self._run_config()
            log_path = Path(tmp_dir) / "build.log"
            with (
                mock.patch(
                    "aicage.registry._local_build.get_agent_build_root",
                    return_value=Path(tmp_dir),
                ),
                mock.patch(
                    "aicage.registry._local_build.subprocess.run",
                    return_value=mock.Mock(returncode=1),
                ) as run_mock,
            ):
                with self.assertRaises(CliError):
                    _local_build._run_build(
                        run_config=run_config,
                        base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                        log_path=log_path,
                    )
        command = run_mock.call_args[0][0]
        self.assertIn("--no-cache", command)

    def test_run_build_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            run_config = self._run_config()
            log_path = Path(tmp_dir) / "build.log"
            with (
                mock.patch(
                    "aicage.registry._local_build.get_agent_build_root",
                    return_value=Path(tmp_dir),
                ),
                mock.patch(
                    "aicage.registry._local_build.subprocess.run",
                    return_value=mock.Mock(returncode=0),
                ) as run_mock,
            ):
                _local_build._run_build(
                    run_config=run_config,
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    log_path=log_path,
                )
            command = run_mock.call_args[0][0]
            self.assertIn("--no-cache", command)
            self.assertTrue(log_path.is_file())

    def test_log_paths_use_timestamp(self) -> None:
        with mock.patch("aicage.registry._local_build._timestamp", return_value="stamp"):
            build_log = _local_build._build_log_path("claude", "ubuntu")
            pull_log = _local_build._pull_log_path("claude", "ubuntu")
        self.assertTrue(str(build_log).endswith("claude-ubuntu-stamp.log"))
        self.assertTrue(str(pull_log).endswith("claude-ubuntu-pull-stamp.log"))

    def test_local_image_exists(self) -> None:
        with mock.patch(
            "aicage.registry._local_build.subprocess.run",
            return_value=mock.Mock(returncode=0),
        ):
            self.assertTrue(_local_build._local_image_exists("aicage:claude-ubuntu"))
        with mock.patch(
            "aicage.registry._local_build.subprocess.run",
            return_value=mock.Mock(returncode=1),
        ):
            self.assertFalse(_local_build._local_image_exists("aicage:claude-ubuntu"))

    def test_should_build_when_base_digest_changes(self) -> None:
        record = _local_build._BuildRecord(
            agent="claude",
            base="ubuntu",
            agent_version="1.2.3",
            base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
            base_digest="sha256:old",
            image_ref="aicage:claude-ubuntu",
            built_at="2024-01-01T00:00:00+00:00",
        )
        run_config = self._run_config()
        with mock.patch("aicage.registry._local_build._local_image_exists", return_value=True):
            should_build = _local_build._should_build(run_config, record, "sha256:new")
        self.assertTrue(should_build)

    def test_should_build_when_record_missing(self) -> None:
        run_config = self._run_config()
        with mock.patch("aicage.registry._local_build._local_image_exists", return_value=True):
            should_build = _local_build._should_build(run_config, None, "sha256:new")
        self.assertTrue(should_build)

    def test_should_build_when_agent_version_changes(self) -> None:
        record = _local_build._BuildRecord(
            agent="claude",
            base="ubuntu",
            agent_version="1.2.2",
            base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
            base_digest="sha256:base",
            image_ref="aicage:claude-ubuntu",
            built_at="2024-01-01T00:00:00+00:00",
        )
        run_config = self._run_config()
        with mock.patch("aicage.registry._local_build._local_image_exists", return_value=True):
            should_build = _local_build._should_build(run_config, record, "sha256:base")
        self.assertTrue(should_build)

    def test_should_build_when_record_missing_digest(self) -> None:
        record = _local_build._BuildRecord(
            agent="claude",
            base="ubuntu",
            agent_version="1.2.3",
            base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
            base_digest=None,
            image_ref="aicage:claude-ubuntu",
            built_at="2024-01-01T00:00:00+00:00",
        )
        run_config = self._run_config()
        with mock.patch("aicage.registry._local_build._local_image_exists", return_value=True):
            should_build = _local_build._should_build(run_config, record, "sha256:base")
        self.assertTrue(should_build)

    def test_build_store_load_ignores_non_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = _local_build._BuildStore(base_dir=Path(tmp_dir))
            record_path = Path(tmp_dir) / "claude-ubuntu.yaml"
            record_path.write_text("- item\n", encoding="utf-8")
            record = store.load("claude", "ubuntu")
        self.assertIsNone(record)

    @staticmethod
    def _run_config() -> RunConfig:
        return RunConfig(
            project_path=Path("/tmp/project"),
            agent="claude",
            base="ubuntu",
            image_ref="aicage:claude-ubuntu",
            agent_version="1.2.3",
            global_cfg=GlobalConfig(
                image_registry="ghcr.io",
                image_registry_api_url="https://ghcr.io/v2",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                image_repository="aicage/aicage",
                image_base_repository="aicage/aicage-image-base",
                default_image_base="ubuntu",
                version_check_image="ghcr.io/aicage/aicage-image-util:latest",
                agents={},
            ),
            images_metadata=LocalBuildTests._images_metadata(),
            project_docker_args="",
            mounts=[],
        )

    @staticmethod
    def _images_metadata() -> ImagesMetadata:
        return ImagesMetadata.from_mapping(
            {
                "aicage-image": {"version": "0.3.3"},
                "aicage-image-base": {"version": "0.3.3"},
                "bases": {
                    "ubuntu": {
                        "root_image": "ubuntu:latest",
                        "base_image_distro": "Ubuntu",
                        "base_image_description": "Default",
                        "os_installer": "distro/debian/install.sh",
                        "test_suite": "default",
                    }
                },
                "agent": {
                    "claude": {
                        "agent_path": "~/.claude",
                        "agent_full_name": "Claude Code",
                        "agent_homepage": "https://example.com",
                        "redistributable": False,
                        "valid_bases": {"ubuntu": "ghcr.io/aicage/aicage:claude-ubuntu"},
                    }
                },
            }
        )
