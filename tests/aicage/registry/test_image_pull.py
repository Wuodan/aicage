import io
import json
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from docker.errors import DockerException

from aicage.config.global_config import GlobalConfig
from aicage.config.runtime_config import RunConfig
from aicage.registry import image_pull
from aicage.registry.images_metadata.models import (
    _AGENT_KEY,
    _AICAGE_IMAGE_BASE_KEY,
    _AICAGE_IMAGE_KEY,
    _BASE_IMAGE_DESCRIPTION_KEY,
    _BASE_IMAGE_DISTRO_KEY,
    _BASES_KEY,
    _OS_INSTALLER_KEY,
    _ROOT_IMAGE_KEY,
    _TEST_SUITE_KEY,
    _VALID_BASES_KEY,
    _VERSION_KEY,
    AGENT_FULL_NAME_KEY,
    AGENT_HOMEPAGE_KEY,
    AGENT_PATH_KEY,
    BUILD_LOCAL_KEY,
    ImagesMetadata,
)


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
    def _build_run_config(self, image_ref: str) -> RunConfig:
        return RunConfig(
            project_path=Path("/tmp/project"),
            agent="codex",
            base="ubuntu",
            image_ref=image_ref,
            base_image_ref=image_ref,
            extensions=[],
            global_cfg=GlobalConfig(
                image_registry="ghcr.io",
                image_registry_api_url="https://ghcr.io/v2",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                image_repository="aicage/aicage",
                image_base_repository="aicage/aicage-image-base",
                default_image_base="ubuntu",
                version_check_image="ghcr.io/aicage/aicage-image-util:agent-version",
                local_image_repository="aicage",
                agents={},
            ),
            images_metadata=self._get_images_metadata(),
            project_docker_args="",
            mounts=[],
        )

    @staticmethod
    def _get_images_metadata() -> ImagesMetadata:
        return ImagesMetadata.from_mapping(
            {
                _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
                _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
                _BASES_KEY: {
                    "ubuntu": {
                        _ROOT_IMAGE_KEY: "ubuntu:latest",
                        _BASE_IMAGE_DISTRO_KEY: "Ubuntu",
                        _BASE_IMAGE_DESCRIPTION_KEY: "Default",
                        _OS_INSTALLER_KEY: "distro/debian/install.sh",
                        _TEST_SUITE_KEY: "default",
                    }
                },
                _AGENT_KEY: {
                    "codex": {
                        AGENT_PATH_KEY: "~/.codex",
                        AGENT_FULL_NAME_KEY: "Codex CLI",
                        AGENT_HOMEPAGE_KEY: "https://example.com",
                        BUILD_LOCAL_KEY: False,
                        _VALID_BASES_KEY: {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                    }
                },
            }
        )

    def test_pull_image_success_writes_log(self) -> None:
        run_config = self._build_run_config("repo:tag")
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
                image_pull.pull_image(run_config)
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
        run_config = self._build_run_config("repo:tag")
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
                    image_pull.pull_image(run_config)
            remote_mock.assert_not_called()

    def test_pull_image_skips_when_up_to_date(self) -> None:
        run_config = self._build_run_config("repo:tag")
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
                image_pull.pull_image(run_config)
            client_mock.assert_not_called()
            self.assertEqual("", stdout.getvalue())

    def test_pull_image_skips_when_remote_unknown(self) -> None:
        run_config = self._build_run_config("repo:tag")
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
                image_pull.pull_image(run_config)
            client_mock.assert_not_called()
            self.assertEqual("", stdout.getvalue())
