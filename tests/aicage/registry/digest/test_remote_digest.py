from unittest import TestCase, mock

from aicage.registry.digest.remote_digest import get_remote_digest


class RemoteDigestTests(TestCase):
    def test_get_remote_digest_returns_digest_reference(self) -> None:
        with (
            mock.patch("aicage.registry.digest._docker_io.get_docker_io_digest") as docker_mock,
            mock.patch("aicage.registry.digest._ghcr.get_ghcr_digest") as ghcr_mock,
        ):
            result = get_remote_digest("ghcr.io/org/repo@sha256:deadbeef")
        self.assertEqual("sha256:deadbeef", result)
        docker_mock.assert_not_called()
        ghcr_mock.assert_not_called()
