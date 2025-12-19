import sys
from typing import List

from aicage.errors import CliError

from ._local import discover_local_bases
from ._remote import RegistryDiscoveryError, discover_base_aliases


def discover_tool_bases(
    repository: str,
    repository_ref: str,
    registry_api_url: str,
    registry_token_url: str,
    tool: str,
) -> List[str]:
    remote_bases: List[str] = []
    local_bases: List[str] = []
    try:
        remote_bases = discover_base_aliases(repository, registry_api_url, registry_token_url, tool)
    except RegistryDiscoveryError as exc:
        print(f"[aicage] Warning: {exc}. Continuing with local images.", file=sys.stderr)
    try:
        local_bases = discover_local_bases(repository_ref, tool)
    except CliError as exc:
        print(f"[aicage] Warning: {exc}", file=sys.stderr)
    return sorted(set(remote_bases) | set(local_bases))
