from unittest import TestCase, mock

from aicage.registry.digest import _docker_io
from aicage.registry.digest._parser import ParsedImageRef


class DockerIoDigestTests(TestCase):
    def test_get_docker_io_digest_returns_none_for_other_registry(self) -> None:
        parsed = ParsedImageRef(
            registry="ghcr.io",
            repository="org/repo",
            reference="latest",
            is_digest=False,
        )
        with mock.patch("aicage.registry.digest._docker_io.get_manifest_digest") as fetch_mock:
            digest = _docker_io.get_docker_io_digest(parsed)
        self.assertIsNone(digest)
        fetch_mock.assert_not_called()
