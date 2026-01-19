from functools import lru_cache

import docker
from docker.client import DockerClient
from docker.errors import DockerException

from .errors import DockerError
from ._timeouts import DOCKER_REQUEST_TIMEOUT_SECONDS


@lru_cache(maxsize=1)
def get_docker_client() -> DockerClient:
    try:
        return docker.from_env(timeout=DOCKER_REQUEST_TIMEOUT_SECONDS)
    except DockerException as exc:
        raise DockerError("Docker is not running or not reachable. Start Docker and retry.") from exc
