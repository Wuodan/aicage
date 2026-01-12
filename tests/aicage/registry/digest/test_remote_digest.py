from unittest import TestCase, mock

from aicage.registry.digest.remote_digest import get_remote_digest


class RemoteDigestTests(TestCase):
    def test_get_remote_digest_returns_digest_reference(self) -> None:
        with (
            mock.patch("aicage.registry.digest.remote_digest.get_docker_io_digest") as docker_mock,
            mock.patch("aicage.registry.digest.remote_digest.get_ghcr_digest") as ghcr_mock,
        ):
            result = get_remote_digest("ghcr.io/org/repo@sha256:deadbeef")
        self.assertEqual("sha256:deadbeef", result)
        docker_mock.assert_not_called()
        ghcr_mock.assert_not_called()

    def test_get_remote_digest_prefers_ghcr(self) -> None:
        with (
            mock.patch("aicage.registry.digest.remote_digest.get_ghcr_digest", return_value="sha256:ghcr"),
            mock.patch("aicage.registry.digest.remote_digest.get_docker_io_digest") as docker_mock,
        ):
            result = get_remote_digest("ghcr.io/org/repo:latest")
        self.assertEqual("sha256:ghcr", result)
        docker_mock.assert_not_called()

    def test_get_remote_digest_falls_back_to_docker_io(self) -> None:
        with (
            mock.patch("aicage.registry.digest.remote_digest.get_ghcr_digest", return_value=None),
            mock.patch(
                "aicage.registry.digest.remote_digest.get_docker_io_digest",
                return_value="sha256:docker",
            ),
        ):
            result = get_remote_digest("ubuntu:latest")
        self.assertEqual("sha256:docker", result)
