import subprocess
from unittest import TestCase, mock

from aicage.errors import CliError
from aicage.registry.discovery import _local as registry_local


class FakeCompleted:
    def __init__(self, stdout: str = "", stderr: str = "", returncode: int = 0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class LocalDiscoveryTests(TestCase):
    def test_discover_local_bases_and_errors(self) -> None:
        list_output = "\n".join(
            [
                "repo:codex-ubuntu-latest",
                "repo:codex-debian-latest",
                "repo:codex-ubuntu-1.0",
                "other:codex-ubuntu-latest",
                "repo:codex-<none>",
            ]
        )
        with mock.patch(
            "aicage.registry.discovery._local.subprocess.run",
            return_value=FakeCompleted(stdout=list_output, returncode=0),
        ):
            aliases = registry_local.discover_local_bases("repo", "codex")
        self.assertEqual(["debian", "ubuntu"], aliases)

        with mock.patch(
            "aicage.registry.discovery._local.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "docker image ls", stderr="boom"),
        ):
            with self.assertRaises(CliError):
                registry_local.discover_local_bases("repo", "codex")
