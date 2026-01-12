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
