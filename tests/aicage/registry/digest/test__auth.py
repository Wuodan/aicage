import json
from unittest import TestCase, mock

from aicage.registry.digest import _auth


class DigestAuthTests(TestCase):
    def test_parse_auth_header_handles_empty_params(self) -> None:
        scheme, params = _auth._parse_auth_header("Bearer")
        self.assertEqual("bearer", scheme)
        self.assertEqual({}, params)

    def test_fetch_bearer_token_returns_none_on_invalid_json(self) -> None:
        response = mock.Mock()
        response.read.return_value = b"not-json"
        response.__enter__ = mock.Mock(return_value=response)
        response.__exit__ = mock.Mock(return_value=None)
        with mock.patch(
            "aicage.registry.digest._auth.urllib.request.urlopen",
            return_value=response,
        ):
            token = _auth._fetch_bearer_token("https://example.test", "", "repo:pull")
        self.assertIsNone(token)

    def test_fetch_bearer_token_returns_none_on_missing_token(self) -> None:
        response = mock.Mock()
        response.read.return_value = json.dumps({"access_token": ""}).encode("utf-8")
        response.__enter__ = mock.Mock(return_value=response)
        response.__exit__ = mock.Mock(return_value=None)
        with mock.patch(
            "aicage.registry.digest._auth.urllib.request.urlopen",
            return_value=response,
        ):
            token = _auth._fetch_bearer_token("https://example.test", "", "repo:pull")
        self.assertIsNone(token)

    def test_fetch_bearer_token_accepts_access_token(self) -> None:
        response = mock.Mock()
        response.read.return_value = json.dumps({"access_token": "token"}).encode("utf-8")
        response.__enter__ = mock.Mock(return_value=response)
        response.__exit__ = mock.Mock(return_value=None)
        with mock.patch(
            "aicage.registry.digest._auth.urllib.request.urlopen",
            return_value=response,
        ):
            token = _auth._fetch_bearer_token("https://example.test", "", "repo:pull")
        self.assertEqual("token", token)
