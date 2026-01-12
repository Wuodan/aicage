from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping

from ._timeouts import REGISTRY_REQUEST_TIMEOUT_SECONDS

_ACCEPT_HEADERS = ",".join(
    [
        "application/vnd.oci.image.index.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        "application/vnd.oci.image.manifest.v1+json",
        "application/vnd.docker.distribution.manifest.v2+json",
    ]
)
_AUTH_HEADER_SPLIT_PARTS: int = 2


def get_manifest_digest(registry: str, repository: str, reference: str) -> str | None:
    url = f"https://{registry}/v2/{repository}/manifests/{reference}"
    headers = {"Accept": _ACCEPT_HEADERS}
    status, response_headers = _head_request(url, headers)
    digest = _read_digest(response_headers)
    if digest:
        return digest
    if status not in {401, 403}:
        return None

    auth_header = _get_header(response_headers, "www-authenticate")
    if not auth_header:
        return None

    scheme, params = _parse_auth_header(auth_header)
    if scheme != "bearer":
        return None
    token = _fetch_bearer_token(
        realm=params.get("realm", ""),
        service=params.get("service", ""),
        scope=params.get("scope") or f"repository:{repository}:pull",
    )
    if not token:
        return None

    auth_headers = {"Accept": _ACCEPT_HEADERS, "Authorization": f"Bearer {token}"}
    _, response_headers = _head_request(url, auth_headers)
    return _read_digest(response_headers)


def _head_request(url: str, headers: Mapping[str, str]) -> tuple[int | None, dict[str, str]]:
    request = urllib.request.Request(url, headers=dict(headers), method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=REGISTRY_REQUEST_TIMEOUT_SECONDS) as response:
            return response.status, dict(response.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers)
    except urllib.error.URLError:
        return None, {}


def _read_digest(headers: Mapping[str, str]) -> str | None:
    digest = _get_header(headers, "docker-content-digest")
    if digest:
        return digest
    return None


def _get_header(headers: Mapping[str, str], key: str) -> str | None:
    for header, value in headers.items():
        if header.lower() == key:
            return value
    return None


def _parse_auth_header(value: str) -> tuple[str, dict[str, str]]:
    parts = value.split(" ", 1)
    if not parts:
        return "", {}
    scheme = parts[0].strip().lower()
    params: dict[str, str] = {}
    if len(parts) == _AUTH_HEADER_SPLIT_PARTS:
        params = dict(re.findall(r'(\w+)="([^"]+)"', parts[1]))
    return scheme, params


def _fetch_bearer_token(realm: str, service: str, scope: str) -> str | None:
    if not realm:
        return None
    query = {"service": service, "scope": scope} if service else {"scope": scope}
    url = f"{realm}?{urllib.parse.urlencode(query)}"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=REGISTRY_REQUEST_TIMEOUT_SECONDS) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.URLError:
        return None
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return None
    token = data.get("token") or data.get("access_token")
    if not isinstance(token, str) or not token:
        return None
    return token
