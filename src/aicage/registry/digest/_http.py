from __future__ import annotations

import urllib.error
import urllib.request
from collections.abc import Mapping

from ._timeouts import REGISTRY_REQUEST_TIMEOUT_SECONDS


def head_request(url: str, headers: Mapping[str, str]) -> tuple[int | None, dict[str, str]]:
    request = urllib.request.Request(url, headers=dict(headers), method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=REGISTRY_REQUEST_TIMEOUT_SECONDS) as response:
            return response.status, dict(response.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers)
    except urllib.error.URLError:
        return None, {}


def get_header(headers: Mapping[str, str], key: str) -> str | None:
    for header, value in headers.items():
        if header.lower() == key:
            return value
    return None
