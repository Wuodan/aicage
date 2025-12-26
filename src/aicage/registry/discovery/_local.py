from docker.errors import DockerException

from aicage.docker_client import get_docker_client
from aicage.errors import CliError


def discover_local_bases(repository_ref: str, tool: str) -> list[str]:
    """
    Fallback discovery using local images when the registry is unavailable.
    """
    try:
        client = get_docker_client()
        images = client.images.list(name=repository_ref)
    except DockerException as exc:
        raise CliError(f"Failed to list local images for {repository_ref}: {exc}") from exc

    aliases: set[str] = set()
    for image in images:
        for image_tag in image.tags:
            stripped_tag = image_tag.strip()
            if not stripped_tag or stripped_tag.endswith(":<none>"):
                continue
            if ":" not in stripped_tag:
                continue
            repo, tag = stripped_tag.split(":", 1)
            if repo != repository_ref:
                continue
            prefix = f"{tool}-"
            suffix = "-latest"
            if tag.startswith(prefix) and tag.endswith(suffix):
                base = tag[len(prefix) : -len(suffix)]
                if base:
                    aliases.add(base)

    return sorted(aliases)
