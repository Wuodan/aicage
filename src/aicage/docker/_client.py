from __future__ import annotations

from functools import lru_cache

import docker
from docker.client import DockerClient


@lru_cache(maxsize=1)
def get_docker_client() -> DockerClient:
    return docker.from_env()
