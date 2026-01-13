from unittest import TestCase, mock

from aicage.docker import _client


class DockerClientTests(TestCase):
    @staticmethod
    def test_get_docker_client_uses_timeout() -> None:
        with mock.patch("aicage.docker._client.docker.from_env") as from_env:
            _client.get_docker_client()

        from_env.assert_called_once_with(timeout=_client.DOCKER_REQUEST_TIMEOUT_SECONDS)
