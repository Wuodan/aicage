from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request

from ._timeouts import REGISTRY_REQUEST_TIMEOUT_SECONDS

_AUTH_HEADER_SPLIT_PARTS: int = 2


def parse_auth_header(value: str) -> tuple[str, dict[str, str]]:
    parts = value.split(" ", 1)
    if not parts:
        return "", {}
    scheme = parts[0].strip().lower()
    params: dict[str, str] = {}
    if len(parts) == _AUTH_HEADER_SPLIT_PARTS:
        params = dict(re.findall(r'(\w+)="([^"]+)"', parts[1]))
    return scheme, params


def fetch_bearer_token(realm: str, service: str, scope: str) -> str | None:
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
