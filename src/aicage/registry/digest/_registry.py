from __future__ import annotations

from collections.abc import Mapping

from ._auth import fetch_bearer_token, parse_auth_header
from ._http import get_header, head_request

_ACCEPT_HEADERS = ",".join(
    [
        "application/vnd.oci.image.index.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        "application/vnd.oci.image.manifest.v1+json",
        "application/vnd.docker.distribution.manifest.v2+json",
    ]
)

def get_manifest_digest(registry: str, repository: str, reference: str) -> str | None:
    url = f"https://{registry}/v2/{repository}/manifests/{reference}"
    headers = {"Accept": _ACCEPT_HEADERS}
    status, response_headers = head_request(url, headers)
    digest = _read_digest(response_headers)
    if digest:
        return digest
    if status not in {401, 403}:
        return None

    auth_header = get_header(response_headers, "www-authenticate")
    if not auth_header:
        return None

    scheme, params = parse_auth_header(auth_header)
    if scheme != "bearer":
        return None
    token = fetch_bearer_token(
        realm=params.get("realm", ""),
        service=params.get("service", ""),
        scope=params.get("scope") or f"repository:{repository}:pull",
    )
    if not token:
        return None

    auth_headers = {"Accept": _ACCEPT_HEADERS, "Authorization": f"Bearer {token}"}
    _, response_headers = head_request(url, auth_headers)
    return _read_digest(response_headers)


def _read_digest(headers: Mapping[str, str]) -> str | None:
    digest = get_header(headers, "docker-content-digest")
    if digest:
        return digest
    return None
