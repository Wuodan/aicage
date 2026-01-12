from __future__ import annotations

import json
import urllib.request
from collections.abc import Mapping
from typing import Any

from ._timeouts import REGISTRY_REQUEST_TIMEOUT_SECONDS
from .errors import RegistryDiscoveryError
from .types import RegistryApiConfig


def _fetch_pull_token_for_repository(api_config: RegistryApiConfig, repository: str) -> str:
    url = f"{api_config.registry_api_token_url}:{repository}:pull"
    data, _ = _fetch_json(url, None)
    token = data.get("token")
    if not token:
        raise RegistryDiscoveryError(f"Missing token while querying registry for {repository}.")
    return token


def _fetch_json(url: str, headers: dict[str, str] | None) -> tuple[dict[str, Any], Mapping[str, str]]:
    request = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=REGISTRY_REQUEST_TIMEOUT_SECONDS) as response:
            payload = response.read().decode("utf-8")
            response_headers = response.headers
    except Exception as exc:  # pylint: disable=broad-except
        raise RegistryDiscoveryError(f"Failed to query registry endpoint {url}: {exc}") from exc

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RegistryDiscoveryError(f"Invalid JSON from registry endpoint {url}: {exc}") from exc
    return data, response_headers
