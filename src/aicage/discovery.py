import json
import urllib.parse
import urllib.request
from typing import List


class DiscoveryError(Exception):
    """Raised when Docker Hub discovery fails."""


def discover_base_aliases(repository: str, tool: str) -> List[str]:
    """
    Query Docker Hub for tags on the given repository and return base aliases derived from
    tags matching '<tool>-<base>-latest'. Mirrors the behavior of aicage-image/scripts/common.sh:
    iterate pagination, collect tag names, and strip the tool prefix and '-latest' suffix.
    """
    aliases: set[str] = set()
    page_url = f"https://hub.docker.com/v2/repositories/{urllib.parse.quote(repository)}/tags?page_size=100"

    while page_url:
        try:
            with urllib.request.urlopen(page_url) as response:
                payload = response.read().decode("utf-8")
        except Exception as exc:  # pylint: disable=broad-except
            raise DiscoveryError(f"Failed to query Docker Hub for {repository}: {exc}") from exc

        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise DiscoveryError(f"Invalid JSON from Docker Hub for {repository}: {exc}") from exc

        for result in data.get("results", []):
            name = result.get("name", "")
            expected_prefix = f"{tool}-"
            if name.startswith(expected_prefix) and name.endswith("-latest"):
                suffix_len = len("-latest")
                base_with_prefix = name[: -suffix_len]
                base = base_with_prefix[len(expected_prefix) :]
                if base:
                    aliases.add(base)

        page_url = data.get("next") or ""

    return sorted(aliases)
