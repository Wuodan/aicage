import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.errors import CliError
from aicage.registry.local_build import _digest

from ._fixtures import build_run_config


class LocalBuildDigestTests(TestCase):
    def test_refresh_base_digest_skips_pull_when_remote_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            global_cfg = build_run_config().global_cfg
            with (
                mock.patch(
                    "aicage.registry.local_build._digest._local_query.get_local_repo_digest_for_repo",
                    return_value="sha256:local",
                ),
                mock.patch(
                    "aicage.registry.local_build._digest._remote_query.get_remote_repo_digest_for_repo",
                    return_value=None,
                ),
                mock.patch("aicage.registry.local_build._digest.subprocess.run") as run_mock,
            ):
                digest = _digest.refresh_base_digest(
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
            global_cfg = build_run_config().global_cfg
            with (
                mock.patch(
                    "aicage.registry.local_build._digest._local_query.get_local_repo_digest_for_repo",
                    return_value="sha256:local",
                ),
                mock.patch(
                    "aicage.registry.local_build._digest._remote_query.get_remote_repo_digest_for_repo",
                    return_value="sha256:remote",
                ),
                mock.patch(
                    "aicage.registry.local_build._digest.subprocess.run",
                    return_value=mock.Mock(returncode=1),
                ),
            ):
                digest = _digest.refresh_base_digest(
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    base_repository="ghcr.io/aicage/aicage-image-base",
                    global_cfg=global_cfg,
                    pull_log_path=log_path,
                )
            self.assertEqual("sha256:local", digest)
            self.assertTrue(log_path.is_file())

    def test_refresh_base_digest_pull_failure_without_local_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            global_cfg = build_run_config().global_cfg
            with (
                mock.patch(
                    "aicage.registry.local_build._digest._local_query.get_local_repo_digest_for_repo",
                    return_value=None,
                ),
                mock.patch(
                    "aicage.registry.local_build._digest._remote_query.get_remote_repo_digest_for_repo",
                    return_value="sha256:remote",
                ),
                mock.patch(
                    "aicage.registry.local_build._digest.subprocess.run",
                    return_value=mock.Mock(returncode=1),
                ),
            ):
                with self.assertRaises(CliError) as exc:
                    _digest.refresh_base_digest(
                        base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                        base_repository="ghcr.io/aicage/aicage-image-base",
                        global_cfg=global_cfg,
                        pull_log_path=log_path,
                    )
            self.assertIn("see", str(exc.exception))
            self.assertTrue(log_path.is_file())

    def test_refresh_base_digest_pull_success_updates_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            global_cfg = build_run_config().global_cfg
            with (
                mock.patch(
                    "aicage.registry.local_build._digest._local_query.get_local_repo_digest_for_repo",
                    side_effect=["sha256:old", "sha256:new"],
                ),
                mock.patch(
                    "aicage.registry.local_build._digest._remote_query.get_remote_repo_digest_for_repo",
                    return_value="sha256:remote",
                ),
                mock.patch(
                    "aicage.registry.local_build._digest.subprocess.run",
                    return_value=mock.Mock(returncode=0),
                ),
            ):
                digest = _digest.refresh_base_digest(
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    base_repository="ghcr.io/aicage/aicage-image-base",
                    global_cfg=global_cfg,
                    pull_log_path=log_path,
                )
            self.assertEqual("sha256:new", digest)
            self.assertTrue(log_path.is_file())
