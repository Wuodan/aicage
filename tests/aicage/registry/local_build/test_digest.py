import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.errors import CliError
from aicage.registry.local_build import _digest

from ._fixtures import build_run_config


class LocalBuildDigestTests(TestCase):
    def test_refresh_base_digest_skips_pull_when_remote_unknown(self) -> None:
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
            mock.patch("aicage.registry.local_build._digest.run_pull") as run_mock,
        ):
            digest = _digest.refresh_base_digest(
                base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                base_repository="ghcr.io/aicage/aicage-image-base",
                global_cfg=global_cfg,
            )
        self.assertEqual("sha256:local", digest)
        run_mock.assert_not_called()

    def test_refresh_base_digest_pull_failure_uses_local_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
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
                    "aicage.registry.local_build._digest.run_pull",
                    side_effect=CliError("docker pull failed"),
                ),
                mock.patch("aicage.registry.local_build._digest.pull_log_path", return_value=Path(tmp_dir)),
            ):
                digest = _digest.refresh_base_digest(
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    base_repository="ghcr.io/aicage/aicage-image-base",
                    global_cfg=global_cfg,
                )
            self.assertEqual("sha256:local", digest)

    def test_refresh_base_digest_pull_failure_without_local_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
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
                    "aicage.registry.local_build._digest.run_pull",
                    side_effect=CliError("docker pull failed"),
                ),
                mock.patch("aicage.registry.local_build._digest.pull_log_path", return_value=Path(tmp_dir)),
            ):
                with self.assertRaises(CliError) as exc:
                    _digest.refresh_base_digest(
                        base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                        base_repository="ghcr.io/aicage/aicage-image-base",
                        global_cfg=global_cfg,
                    )
            self.assertIn("docker pull failed", str(exc.exception))

    def test_refresh_base_digest_pull_success_updates_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
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
                    "aicage.registry.local_build._digest.run_pull",
                    return_value=None,
                ),
                mock.patch("aicage.registry.local_build._digest.pull_log_path", return_value=Path(tmp_dir)),
            ):
                digest = _digest.refresh_base_digest(
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    base_repository="ghcr.io/aicage/aicage-image-base",
                    global_cfg=global_cfg,
                )
            self.assertEqual("sha256:new", digest)
