import urllib.error
from email.message import Message
from unittest import TestCase, mock

from aicage.docker import remote_query
from aicage.docker._registry_api import RegistryDiscoveryError
from aicage.docker.types import ImageRefRepository, RegistryApiConfig, RemoteImageRef


class FakeResponse:
    def __init__(self, headers: dict[str, str], payload: str = "") -> None:
        self.headers = headers
        self._payload = payload

    def read(self) -> bytes:
        return self._payload.encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class RemoteQueryTests(TestCase):
    def test_get_remote_repo_digest_returns_none_on_token_error(self) -> None:
        with (
            mock.patch(
                "aicage.docker.remote_query.fetch_pull_token_for_repository",
                side_effect=RegistryDiscoveryError("boom"),
            ),
            mock.patch("aicage.docker.remote_query.urllib.request.urlopen") as urlopen_mock,
        ):
            digest = remote_query.get_remote_repo_digest(self._remote_image())
        self.assertIsNone(digest)
        urlopen_mock.assert_not_called()

    def test_get_remote_repo_digest_with_token(self) -> None:
        with (
            mock.patch(
                "aicage.docker.remote_query.fetch_pull_token_for_repository",
                return_value="abc",
            ),
            mock.patch(
                "aicage.docker.remote_query.urllib.request.urlopen",
                return_value=FakeResponse({"Docker-Content-Digest": "sha256:remote"}),
            ),
        ):
            digest = remote_query.get_remote_repo_digest(self._remote_image())
        self.assertEqual("sha256:remote", digest)

    def test_get_remote_repo_digest_returns_none_on_missing_reference(self) -> None:
        with mock.patch(
            "aicage.docker.remote_query.fetch_pull_token_for_repository",
        ) as token_mock:
            digest = remote_query.get_remote_repo_digest(self._remote_image(image_ref="ghcr.io/aicage/aicage"))
        self.assertIsNone(digest)
        token_mock.assert_not_called()

    def test_get_remote_repo_digest_returns_none_on_missing_headers(self) -> None:
        with (
            mock.patch(
                "aicage.docker.remote_query.fetch_pull_token_for_repository",
                return_value="abc",
            ),
            mock.patch(
                "aicage.docker.remote_query._head_request",
                return_value=None,
            ),
        ):
            digest = remote_query.get_remote_repo_digest(self._remote_image())
        self.assertIsNone(digest)

    def test_get_remote_repo_digest_accepts_lowercase_header(self) -> None:
        with (
            mock.patch(
                "aicage.docker.remote_query.fetch_pull_token_for_repository",
                return_value="abc",
            ),
            mock.patch(
                "aicage.docker.remote_query._head_request",
                return_value={"docker-content-digest": "sha256:lower"},
            ),
        ):
            digest = remote_query.get_remote_repo_digest(self._remote_image())
        self.assertEqual("sha256:lower", digest)

    def test_parse_reference_accepts_digest(self) -> None:
        reference = remote_query._parse_reference("ghcr.io/aicage/aicage@sha256:abc")
        self.assertEqual("sha256:abc", reference)

    def test_parse_reference_accepts_tag(self) -> None:
        reference = remote_query._parse_reference("ghcr.io/aicage/aicage:tag")
        self.assertEqual("tag", reference)

    def test_parse_reference_rejects_missing_tag(self) -> None:
        reference = remote_query._parse_reference("ghcr.io/aicage/aicage")
        self.assertIsNone(reference)

    def test_parse_reference_rejects_empty_tag(self) -> None:
        reference = remote_query._parse_reference("ghcr.io/aicage/aicage:")
        self.assertIsNone(reference)

    def test_head_request_returns_headers_on_auth_error(self) -> None:
        headers = Message()
        headers["Docker-Content-Digest"] = "sha256:abc"
        error = urllib.error.HTTPError(
            url="https://example.test",
            code=401,
            msg="unauthorized",
            hdrs=headers,
            fp=None,
        )
        with mock.patch(
            "aicage.docker.remote_query.urllib.request.urlopen",
            side_effect=error,
        ):
            result = remote_query._head_request("https://example.test", {"Accept": "x"})
        self.assertEqual({"Docker-Content-Digest": "sha256:abc"}, result)

    def test_head_request_returns_none_on_other_errors(self) -> None:
        headers = Message()
        error = urllib.error.HTTPError(
            url="https://example.test",
            code=404,
            msg="missing",
            hdrs=headers,
            fp=None,
        )
        with mock.patch(
            "aicage.docker.remote_query.urllib.request.urlopen",
            side_effect=error,
        ):
            result = remote_query._head_request("https://example.test", {"Accept": "x"})
        self.assertIsNone(result)

    def test_head_request_returns_none_on_url_error(self) -> None:
        with mock.patch(
            "aicage.docker.remote_query.urllib.request.urlopen",
            side_effect=urllib.error.URLError("boom"),
        ):
            result = remote_query._head_request("https://example.test", {"Accept": "x"})
        self.assertIsNone(result)

    @staticmethod
    def _remote_image(image_ref: str = "ghcr.io/aicage/aicage:tag") -> RemoteImageRef:
        return RemoteImageRef(
            image=ImageRefRepository(
                image_ref=image_ref,
                repository="aicage/aicage",
            ),
            registry_api=RegistryApiConfig(
                registry_api_url="https://ghcr.io/v2",
                registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
            ),
        )
