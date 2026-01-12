from unittest import TestCase, mock

from aicage.registry.digest import _registry as registry


class RegistryDigestTests(TestCase):

    def test_get_manifest_digest_reads_direct_digest(self) -> None:
        with (
            mock.patch(
                "aicage.registry.digest._registry._head_request",
                return_value=(200, {"Docker-Content-Digest": "sha256:abc"}),
            ),
            mock.patch("aicage.registry.digest._registry._fetch_bearer_token") as token_mock,
        ):
            digest = registry.get_manifest_digest("ghcr.io", "org/repo", "latest")
        self.assertEqual("sha256:abc", digest)
        token_mock.assert_not_called()

    def test_get_manifest_digest_uses_bearer_challenge(self) -> None:
        auth_header = 'Bearer realm="https://example.com/token",service="ghcr.io",scope="repo:pull"'
        head_responses = [
            (401, {"WWW-Authenticate": auth_header}),
            (200, {"docker-content-digest": "sha256:def"}),
        ]
        with (
            mock.patch(
                "aicage.registry.digest._registry._head_request",
                side_effect=head_responses,
            ),
            mock.patch(
                "aicage.registry.digest._registry._fetch_bearer_token",
                return_value="token",
            ) as token_mock,
        ):
            digest = registry.get_manifest_digest("ghcr.io", "org/repo", "latest")
        self.assertEqual("sha256:def", digest)
        token_mock.assert_called_once()
