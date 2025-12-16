import io
import subprocess
from unittest import TestCase, mock

from aicage.errors import CliError
from aicage.runtime import base_image


class FakeCompleted:
    def __init__(self, stdout: str = "", stderr: str = "", returncode: int = 0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class DockerInvocationTests(TestCase):
    def test_pull_image_success_and_warning(self) -> None:
        pull_ok = FakeCompleted(returncode=0)
        with mock.patch("aicage.runtime.base_image.subprocess.run", return_value=pull_ok) as run_mock:
            base_image._pull_image("repo:tag")
        run_mock.assert_called_once_with(["docker", "pull", "repo:tag"], capture_output=True, text=True)

        pull_fail = FakeCompleted(returncode=1, stderr="timeout")
        inspect_ok = FakeCompleted(returncode=0)
        with mock.patch("aicage.runtime.base_image.subprocess.run", side_effect=[pull_fail, inspect_ok]):
            with mock.patch("sys.stderr", new_callable=io.StringIO) as stderr:
                base_image._pull_image("repo:tag")
        self.assertIn("Warning", stderr.getvalue())

    def test_pull_image_raises_on_missing_local(self) -> None:
        pull_fail = FakeCompleted(returncode=1, stderr="network down", stdout="")
        inspect_fail = FakeCompleted(returncode=1, stderr="missing", stdout="")
        with mock.patch("aicage.runtime.base_image.subprocess.run", side_effect=[pull_fail, inspect_fail]):
            with self.assertRaises(CliError):
                base_image._pull_image("repo:tag")

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
        with mock.patch("aicage.runtime.base_image.subprocess.run", return_value=FakeCompleted(stdout=list_output, returncode=0)):
            aliases = base_image._discover_local_bases("repo", "codex")
        self.assertEqual(["debian", "ubuntu"], aliases)

        with mock.patch(
            "aicage.runtime.base_image.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "docker image ls", stderr="boom"),
        ):
            with self.assertRaises(CliError):
                base_image._discover_local_bases("repo", "codex")
