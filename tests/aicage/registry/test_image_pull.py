import io
import json
from unittest import TestCase, mock

from aicage.errors import CliError
from aicage.registry import image_pull


class FakeCompleted:
    def __init__(self, stdout: str = "", stderr: str = "", returncode: int = 0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class FakeProcess:
    def __init__(self, output: str = "", returncode: int = 0) -> None:
        self.stdout = io.StringIO(output)
        self.returncode = returncode

    def wait(self) -> int:
        return self.returncode


class DockerInvocationTests(TestCase):
    def test_pull_image_success_and_warning(self) -> None:
        pull_ok = FakeProcess(
            output="repo:tag\n",
            returncode=0,
        )
        with (
            mock.patch("aicage.registry.image_pull._get_local_repo_digest", return_value=None),
            mock.patch("aicage.registry.image_pull._get_remote_manifest_digests") as remote_mock,
            mock.patch("aicage.registry.image_pull.subprocess.Popen", return_value=pull_ok) as popen_mock,
            mock.patch("aicage.registry.image_pull.subprocess.run") as run_mock,
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            image_pull.pull_image("repo:tag")
        remote_mock.assert_not_called()
        popen_mock.assert_called_once()
        run_mock.assert_not_called()
        self.assertIn("Pulling image repo:tag", stdout.getvalue())

        pull_download = FakeProcess(
            output=(
                "repo:tag: Pulling from org/repo\n"
                "abc123: Pulling fs layer\n"
                "abc123: Downloading\n"
                "Status: Downloaded newer image for repo:tag\n"
            ),
            returncode=0,
        )
        with (
            mock.patch("aicage.registry.image_pull._get_local_repo_digest", return_value=None),
            mock.patch("aicage.registry.image_pull._get_remote_manifest_digests") as remote_mock,
            mock.patch("aicage.registry.image_pull.subprocess.Popen", return_value=pull_download) as popen_mock,
            mock.patch("aicage.registry.image_pull.subprocess.run") as run_mock,
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            image_pull.pull_image("repo:tag")
        remote_mock.assert_not_called()
        popen_mock.assert_called_once()
        run_mock.assert_not_called()
        output = stdout.getvalue()
        self.assertIn("Pulling image repo:tag", output)
        self.assertIn("Pulling fs layer", output)

        pull_fail = FakeProcess(output="timeout\n", returncode=1)
        inspect_ok = FakeCompleted(returncode=0)
        with (
            mock.patch("aicage.registry.image_pull._get_local_repo_digest", return_value=None),
            mock.patch("aicage.registry.image_pull._get_remote_manifest_digests") as remote_mock,
            mock.patch("aicage.registry.image_pull.subprocess.Popen", return_value=pull_fail),
            mock.patch("aicage.registry.image_pull.subprocess.run", return_value=inspect_ok),
            mock.patch("sys.stderr", new_callable=io.StringIO) as stderr,
            mock.patch("sys.stdout", new_callable=io.StringIO),
        ):
            image_pull.pull_image("repo:tag")
        remote_mock.assert_not_called()
        self.assertIn("Warning", stderr.getvalue())

    def test_pull_image_raises_on_missing_local(self) -> None:
        pull_fail = FakeProcess(output="network down\n", returncode=1)
        inspect_fail = FakeCompleted(returncode=1, stderr="missing", stdout="")
        with (
            mock.patch("aicage.registry.image_pull._get_local_repo_digest", return_value=None),
            mock.patch("aicage.registry.image_pull._get_remote_manifest_digests") as remote_mock,
            mock.patch("aicage.registry.image_pull.subprocess.Popen", return_value=pull_fail),
            mock.patch("aicage.registry.image_pull.subprocess.run", return_value=inspect_fail),
            mock.patch("sys.stdout", new_callable=io.StringIO),
        ):
            with self.assertRaises(CliError):
                image_pull.pull_image("repo:tag")
        remote_mock.assert_not_called()

    def test_pull_image_skips_when_up_to_date(self) -> None:
        with (
            mock.patch("aicage.registry.image_pull._get_local_repo_digest", return_value="same"),
            mock.patch("aicage.registry.image_pull._get_remote_manifest_digests", return_value={"same"}),
            mock.patch("aicage.registry.image_pull.subprocess.Popen") as popen_mock,
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            image_pull.pull_image("repo:tag")
        popen_mock.assert_not_called()
        self.assertEqual("", stdout.getvalue())

    def test_pull_image_skips_when_remote_unknown(self) -> None:
        with (
            mock.patch("aicage.registry.image_pull._get_local_repo_digest", return_value="local"),
            mock.patch("aicage.registry.image_pull._get_remote_manifest_digests", return_value=None),
            mock.patch("aicage.registry.image_pull.subprocess.Popen") as popen_mock,
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            image_pull.pull_image("repo:tag")
        popen_mock.assert_not_called()
        self.assertEqual("", stdout.getvalue())


class DigestParsingTests(TestCase):
    def test_repository_from_ref(self) -> None:
        self.assertEqual("repo", image_pull._repository_from_ref("repo:tag"))
        self.assertEqual("repo/name", image_pull._repository_from_ref("repo/name:tag"))
        self.assertEqual("repo/name", image_pull._repository_from_ref("repo/name@sha256:deadbeef"))
        self.assertEqual("localhost:5000/repo", image_pull._repository_from_ref("localhost:5000/repo:tag"))

    def test_get_local_repo_digest(self) -> None:
        with mock.patch(
            "aicage.registry.image_pull.subprocess.run",
            return_value=FakeCompleted(returncode=1, stdout=""),
        ):
            self.assertIsNone(image_pull._get_local_repo_digest("repo:tag"))

        with mock.patch(
            "aicage.registry.image_pull.subprocess.run",
            return_value=FakeCompleted(returncode=0, stdout="not-json"),
        ):
            self.assertIsNone(image_pull._get_local_repo_digest("repo:tag"))

        with mock.patch(
            "aicage.registry.image_pull.subprocess.run",
            return_value=FakeCompleted(returncode=0, stdout='{"bad": "data"}'),
        ):
            self.assertIsNone(image_pull._get_local_repo_digest("repo:tag"))

        payload = '["repo@sha256:deadbeef", "other@sha256:skip"]'
        with mock.patch(
            "aicage.registry.image_pull.subprocess.run",
            return_value=FakeCompleted(returncode=0, stdout=payload),
        ):
            digest = image_pull._get_local_repo_digest("repo:tag")
        self.assertEqual("sha256:deadbeef", digest)

    def test_get_remote_manifest_digests(self) -> None:
        with mock.patch(
            "aicage.registry.image_pull.subprocess.run",
            return_value=FakeCompleted(returncode=1, stdout=""),
        ):
            self.assertIsNone(image_pull._get_remote_manifest_digests("repo:tag"))

        with mock.patch(
            "aicage.registry.image_pull.subprocess.run",
            return_value=FakeCompleted(returncode=0, stdout="not-json"),
        ):
            self.assertIsNone(image_pull._get_remote_manifest_digests("repo:tag"))

        payload = {
            "Descriptor": {"digest": "sha256:one"},
            "config": {"digest": "sha256:cfg"},
            "manifests": [{"digest": "sha256:two"}],
        }
        with mock.patch(
            "aicage.registry.image_pull.subprocess.run",
            return_value=FakeCompleted(returncode=0, stdout=json.dumps(payload)),
        ):
            digests = image_pull._get_remote_manifest_digests("repo:tag")
        self.assertEqual({"sha256:one", "sha256:cfg", "sha256:two"}, digests)

        list_payload = [
            {"Descriptor": {"digest": "sha256:list-one"}},
            {"config": {"digest": "sha256:list-two"}},
        ]
        with mock.patch(
            "aicage.registry.image_pull.subprocess.run",
            return_value=FakeCompleted(returncode=0, stdout=json.dumps(list_payload)),
        ):
            digests = image_pull._get_remote_manifest_digests("repo:tag")
        self.assertEqual({"sha256:list-one", "sha256:list-two"}, digests)
