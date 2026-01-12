from unittest import TestCase, mock

from aicage.registry.digest import _ghcr
from aicage.registry.digest._parser import ParsedImageRef


class GhcrDigestTests(TestCase):
    def test_get_ghcr_digest_returns_none_for_other_registry(self) -> None:
        parsed = ParsedImageRef(
            registry="registry-1.docker.io",
            repository="library/ubuntu",
            reference="latest",
            is_digest=False,
        )
        with mock.patch("aicage.registry.digest._ghcr.get_manifest_digest") as fetch_mock:
            digest = _ghcr.get_ghcr_digest(parsed)
        self.assertIsNone(digest)
        fetch_mock.assert_not_called()

    def test_get_ghcr_digest_fetches_manifest(self) -> None:
        parsed = ParsedImageRef(
            registry="ghcr.io",
            repository="org/repo",
            reference="v1",
            is_digest=False,
        )
        with mock.patch(
            "aicage.registry.digest._ghcr.get_manifest_digest",
            return_value="sha256:def",
        ) as fetch_mock:
            digest = _ghcr.get_ghcr_digest(parsed)
        self.assertEqual("sha256:def", digest)
        fetch_mock.assert_called_once_with("ghcr.io", "org/repo", "v1")
