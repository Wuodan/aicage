import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.registry._errors import RegistryError
from aicage.registry.local_build import _digest


class LocalBuildDigestTests(TestCase):
    def test_refresh_base_digest_skips_pull_when_local_matches_remote(self) -> None:
        with (
            mock.patch(
                "aicage.registry.local_build._digest.get_local_repo_digest_for_repo",
                return_value="sha256:local",
            ),
            mock.patch(
                "aicage.registry.local_build._digest.resolve_verified_digest",
                return_value="ghcr.io/aicage/aicage-image-base@sha256:local",
            ),
            mock.patch("aicage.registry.local_build._digest.run_pull") as run_mock,
        ):
            digest = _digest.refresh_base_digest(
                base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                base_repository="ghcr.io/aicage/aicage-image-base",
            )
        self.assertEqual("ghcr.io/aicage/aicage-image-base@sha256:local", digest)
        run_mock.assert_not_called()

    def test_refresh_base_digest_pull_failure_uses_local_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            with (
                mock.patch(
                    "aicage.registry.local_build._digest.get_local_repo_digest_for_repo",
                    return_value="sha256:local",
                ),
                mock.patch(
                    "aicage.registry.local_build._digest.resolve_verified_digest",
                    return_value="ghcr.io/aicage/aicage-image-base@sha256:remote",
                ),
                mock.patch(
                    "aicage.registry.local_build._digest.run_pull",
                    side_effect=RegistryError("docker pull failed"),
                ),
                mock.patch("aicage.registry.local_build._digest.pull_log_path", return_value=Path(tmp_dir)),
            ):
                digest = _digest.refresh_base_digest(
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    base_repository="ghcr.io/aicage/aicage-image-base",
                )
            self.assertEqual("ghcr.io/aicage/aicage-image-base@sha256:local", digest)

    def test_refresh_base_digest_pull_failure_without_local_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            with (
                mock.patch(
                    "aicage.registry.local_build._digest.get_local_repo_digest_for_repo",
                    return_value=None,
                ),
                mock.patch(
                    "aicage.registry.local_build._digest.resolve_verified_digest",
                    return_value="ghcr.io/aicage/aicage-image-base@sha256:remote",
                ),
                mock.patch(
                    "aicage.registry.local_build._digest.run_pull",
                    side_effect=RegistryError("docker pull failed"),
                ),
                mock.patch("aicage.registry.local_build._digest.pull_log_path", return_value=Path(tmp_dir)),
            ):
                with self.assertRaises(RegistryError) as exc:
                    _digest.refresh_base_digest(
                        base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                        base_repository="ghcr.io/aicage/aicage-image-base",
                    )
            self.assertIn("docker pull failed", str(exc.exception))

    def test_refresh_base_digest_pull_success_updates_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            with (
                mock.patch(
                    "aicage.registry.local_build._digest.get_local_repo_digest_for_repo",
                    return_value="sha256:old",
                ),
                mock.patch(
                    "aicage.registry.local_build._digest.resolve_verified_digest",
                    return_value="ghcr.io/aicage/aicage-image-base@sha256:remote",
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
                )
            self.assertEqual("ghcr.io/aicage/aicage-image-base@sha256:remote", digest)
