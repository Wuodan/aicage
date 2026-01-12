import urllib.error
from unittest import TestCase, mock

from aicage.registry.digest import _http


class DigestHttpTests(TestCase):
    def test_head_request_returns_none_on_url_error(self) -> None:
        with mock.patch(
            "aicage.registry.digest._http.urllib.request.urlopen",
            side_effect=urllib.error.URLError("boom"),
        ):
            status, headers = _http.head_request("https://example.test", {"Accept": "x"})
        self.assertIsNone(status)
        self.assertEqual({}, headers)
