from unittest import TestCase, mock

from docker.errors import DockerException

from aicage.docker import _client
from aicage.docker.errors import DockerError


class DockerClientTests(TestCase):
    def setUp(self) -> None:
        _client.get_docker_client.cache_clear()

    @staticmethod
    def test_get_docker_client_uses_timeout() -> None:
        with mock.patch("aicage.docker._client.docker.from_env") as from_env:
            _client.get_docker_client()

        from_env.assert_called_once_with(timeout=_client.DOCKER_REQUEST_TIMEOUT_SECONDS)

    def test_get_docker_client_raises_clean_error_when_docker_missing(self) -> None:
        with mock.patch(
            "aicage.docker._client.docker.from_env",
            side_effect=DockerException("boom"),
        ):
            with self.assertRaises(DockerError) as raised:
                _client.get_docker_client()

        self.assertEqual(
            "Docker is not running or not reachable. Start Docker and retry.",
            str(raised.exception),
        )
