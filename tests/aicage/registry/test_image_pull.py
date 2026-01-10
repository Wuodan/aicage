import io
import json
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from docker.errors import DockerException

from aicage.config.global_config import GlobalConfig
from aicage.registry import image_pull


class FakeDockerApi:
    def __init__(self, events: list[object], exc: Exception | None = None) -> None:
        self._events = events
        self._exc = exc
        self.calls: list[tuple[str, bool, bool]] = []

    def pull(self, image_ref: str, stream: bool, decode: bool) -> list[object]:
        self.calls.append((image_ref, stream, decode))
        if self._exc is not None:
            raise self._exc
        return list(self._events)


class FakeDockerClient:
    def __init__(self, api: FakeDockerApi) -> None:
        self.api = api


class DockerInvocationTests(TestCase):
    @staticmethod
    def _build_global_cfg() -> GlobalConfig:
        return GlobalConfig(
            image_registry="ghcr.io",
            image_registry_api_url="https://ghcr.io/v2",
            image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
            image_repository="aicage/aicage",
            image_base_repository="aicage/aicage-image-base",
            default_image_base="ubuntu",
            version_check_image="ghcr.io/aicage/aicage-image-util:agent-version",
            local_image_repository="aicage",
            agents={},
        )


    def test_pull_image_success_writes_log(self) -> None:
        image_ref = "repo:tag"
        global_cfg = self._build_global_cfg()
        api = FakeDockerApi(
            events=[
                {"status": "Pulling from org/repo", "id": "repo:tag"},
                {"status": "Downloading", "id": "abc123"},
            ]
        )
        client = FakeDockerClient(api)
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry._pull_decision.get_local_repo_digest",
                    return_value=None,
                ),
                mock.patch(
                    "aicage.registry._pull_decision.get_remote_repo_digest"
                ) as remote_mock,
                mock.patch(
                    "aicage.docker.pull.get_docker_client",
                    return_value=client,
                ),
                mock.patch("aicage.registry.image_pull.pull_log_path", return_value=log_path),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                image_pull.pull_image(image_ref, global_cfg)
            remote_mock.assert_not_called()
            self.assertIn("Pulling image repo:tag", stdout.getvalue())
            log_lines = log_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(2, len(log_lines))
            self.assertEqual(
                {"status": "Pulling from org/repo", "id": "repo:tag"},
                json.loads(log_lines[0]),
            )
            self.assertEqual(
                {"status": "Downloading", "id": "abc123"},
                json.loads(log_lines[1]),
            )
            self.assertEqual([("repo:tag", True, True)], api.calls)

    def test_pull_image_raises_on_sdk_error(self) -> None:
        image_ref = "repo:tag"
        global_cfg = self._build_global_cfg()
        api = FakeDockerApi(events=[], exc=DockerException("network down"))
        client = FakeDockerClient(api)
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry._pull_decision.get_local_repo_digest",
                    return_value=None,
                ),
                mock.patch(
                    "aicage.registry._pull_decision.get_remote_repo_digest"
                ) as remote_mock,
                mock.patch(
                    "aicage.docker.pull.get_docker_client",
                    return_value=client,
                ),
                mock.patch("aicage.registry.image_pull.pull_log_path", return_value=log_path),
                mock.patch("sys.stdout", new_callable=io.StringIO),
            ):
                with self.assertRaises(DockerException):
                    image_pull.pull_image(image_ref, global_cfg)
            remote_mock.assert_not_called()

    def test_pull_image_skips_when_up_to_date(self) -> None:
        image_ref = "repo:tag"
        global_cfg = self._build_global_cfg()
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry._pull_decision.get_local_repo_digest",
                    return_value="same",
                ),
                mock.patch(
                    "aicage.registry._pull_decision.get_remote_repo_digest",
                    return_value="same",
                ),
                mock.patch("aicage.docker.pull.get_docker_client") as client_mock,
                mock.patch("aicage.registry.image_pull.pull_log_path", return_value=log_path),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                image_pull.pull_image(image_ref, global_cfg)
            client_mock.assert_not_called()
            self.assertEqual("", stdout.getvalue())

    def test_pull_image_skips_when_remote_unknown(self) -> None:
        image_ref = "repo:tag"
        global_cfg = self._build_global_cfg()
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry._pull_decision.get_local_repo_digest",
                    return_value="local",
                ),
                mock.patch(
                    "aicage.registry._pull_decision.get_remote_repo_digest",
                    return_value=None,
                ),
                mock.patch("aicage.docker.pull.get_docker_client") as client_mock,
                mock.patch("aicage.registry.image_pull.pull_log_path", return_value=log_path),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                image_pull.pull_image(image_ref, global_cfg)
            client_mock.assert_not_called()
            self.assertEqual("", stdout.getvalue())
