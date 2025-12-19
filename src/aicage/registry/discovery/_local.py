import subprocess
from typing import List

from aicage.errors import CliError


def discover_local_bases(repository_ref: str, tool: str) -> List[str]:
    """
    Fallback discovery using local images when the registry is unavailable.
    """
    try:
        result = subprocess.run(
            ["docker", "image", "ls", repository_ref, "--format", "{{.Repository}}:{{.Tag}}"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise CliError(f"Failed to list local images for {repository_ref}: {exc.stderr or exc}") from exc

    aliases: set[str] = set()
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or line.endswith(":<none>"):
            continue
        if ":" not in line:
            continue
        repo, tag = line.split(":", 1)
        if repo != repository_ref:
            continue
        prefix = f"{tool}-"
        suffix = "-latest"
        if tag.startswith(prefix) and tag.endswith(suffix):
            base = tag[len(prefix) : -len(suffix)]
            if base:
                aliases.add(base)

    return sorted(aliases)
