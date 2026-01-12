import json
from unittest import TestCase, mock

import urllib.error

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

    def test_get_manifest_digest_returns_none_on_non_auth_failure(self) -> None:
        with mock.patch(
            "aicage.registry.digest._registry._head_request",
            return_value=(404, {}),
        ):
            digest = registry.get_manifest_digest("ghcr.io", "org/repo", "latest")
        self.assertIsNone(digest)

    def test_get_manifest_digest_returns_none_when_missing_auth_header(self) -> None:
        with mock.patch(
            "aicage.registry.digest._registry._head_request",
            return_value=(401, {}),
        ):
            digest = registry.get_manifest_digest("ghcr.io", "org/repo", "latest")
        self.assertIsNone(digest)

    def test_get_manifest_digest_returns_none_for_basic_auth(self) -> None:
        with mock.patch(
            "aicage.registry.digest._registry._head_request",
            return_value=(401, {"WWW-Authenticate": "Basic realm=\"x\""}),
        ):
            digest = registry.get_manifest_digest("ghcr.io", "org/repo", "latest")
        self.assertIsNone(digest)

    def test_get_manifest_digest_returns_none_when_token_missing(self) -> None:
        auth_header = 'Bearer realm="https://example.com/token",service="ghcr.io"'
        with (
            mock.patch(
                "aicage.registry.digest._registry._head_request",
                return_value=(401, {"WWW-Authenticate": auth_header}),
            ),
            mock.patch(
                "aicage.registry.digest._registry._fetch_bearer_token",
                return_value=None,
            ),
        ):
            digest = registry.get_manifest_digest("ghcr.io", "org/repo", "latest")
        self.assertIsNone(digest)

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

    def test_parse_auth_header_handles_empty_params(self) -> None:
        scheme, params = registry._parse_auth_header("Bearer")
        self.assertEqual("bearer", scheme)
        self.assertEqual({}, params)

    def test_read_digest_accepts_lowercase_header(self) -> None:
        digest = registry._read_digest({"docker-content-digest": "sha256:abc"})
        self.assertEqual("sha256:abc", digest)

    def test_fetch_bearer_token_returns_none_on_invalid_json(self) -> None:
        response = mock.Mock()
        response.read.return_value = b"not-json"
        response.__enter__ = mock.Mock(return_value=response)
        response.__exit__ = mock.Mock(return_value=None)
        with mock.patch(
            "aicage.registry.digest._registry.urllib.request.urlopen",
            return_value=response,
        ):
            token = registry._fetch_bearer_token("https://example.test", "", "repo:pull")
        self.assertIsNone(token)

    def test_fetch_bearer_token_returns_none_on_missing_token(self) -> None:
        response = mock.Mock()
        response.read.return_value = json.dumps({"access_token": ""}).encode("utf-8")
        response.__enter__ = mock.Mock(return_value=response)
        response.__exit__ = mock.Mock(return_value=None)
        with mock.patch(
            "aicage.registry.digest._registry.urllib.request.urlopen",
            return_value=response,
        ):
            token = registry._fetch_bearer_token("https://example.test", "", "repo:pull")
        self.assertIsNone(token)

    def test_fetch_bearer_token_accepts_access_token(self) -> None:
        response = mock.Mock()
        response.read.return_value = json.dumps({"access_token": "token"}).encode("utf-8")
        response.__enter__ = mock.Mock(return_value=response)
        response.__exit__ = mock.Mock(return_value=None)
        with mock.patch(
            "aicage.registry.digest._registry.urllib.request.urlopen",
            return_value=response,
        ):
            token = registry._fetch_bearer_token("https://example.test", "", "repo:pull")
        self.assertEqual("token", token)

    def test_head_request_returns_none_on_url_error(self) -> None:
        with mock.patch(
            "aicage.registry.digest._registry.urllib.request.urlopen",
            side_effect=urllib.error.URLError("boom"),
        ):
            status, headers = registry._head_request("https://example.test", {"Accept": "x"})
        self.assertIsNone(status)
        self.assertEqual({}, headers)
