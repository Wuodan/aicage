from aicage.errors import AicageError


class DockerError(AicageError):
    pass


class RegistryDiscoveryError(DockerError):
    """Raised when registry discovery fails."""
