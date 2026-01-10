from __future__ import annotations

from functools import lru_cache

import docker
from docker.client import DockerClient

from ._timeouts import DOCKER_REQUEST_TIMEOUT_SECONDS


@lru_cache(maxsize=1)
def get_docker_client() -> DockerClient:
    return docker.from_env(timeout=DOCKER_REQUEST_TIMEOUT_SECONDS)
