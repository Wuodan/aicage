from unittest import TestCase, mock

from docker.errors import DockerException

from aicage.errors import CliError
from aicage.registry.discovery import _local as registry_local


class FakeImage:
    def __init__(self, tags: list[str]):
        self.tags = tags


class FakeImages:
    def __init__(self, images: list[FakeImage]):
        self._images = images

    def list(self, name: str) -> list[FakeImage]:
        return self._images


class FakeClient:
    def __init__(self, images: list[FakeImage]):
        self.images = FakeImages(images)


class LocalDiscoveryTests(TestCase):
    def test_discover_local_bases_and_errors(self) -> None:
        image_tags = [
            "repo:codex-ubuntu-latest",
            "repo:codex-debian-latest",
            "repo:codex-ubuntu-1.0",
            "other:codex-ubuntu-latest",
            "repo:codex-<none>",
        ]
        with mock.patch(
            "aicage.registry.discovery._local.get_docker_client",
            return_value=FakeClient([FakeImage(image_tags)]),
        ):
            aliases = registry_local.discover_local_bases("repo", "codex")
        self.assertEqual(["debian", "ubuntu"], aliases)

        with mock.patch(
            "aicage.registry.discovery._local.get_docker_client",
            side_effect=DockerException("boom"),
        ):
            with self.assertRaises(CliError):
                registry_local.discover_local_bases("repo", "codex")
