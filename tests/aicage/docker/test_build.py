import tempfile
from pathlib import Path
from subprocess import CompletedProcess
from unittest import TestCase, mock

from aicage.config.context import ConfigContext
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.global_config import GlobalConfig
from aicage.config.images_metadata.models import ImagesMetadata, _ImageReleaseInfo
from aicage.config.project_config import ProjectConfig
from aicage.config.runtime_config import RunConfig
from aicage.docker import build
from aicage.docker.errors import DockerError
from aicage.paths import DEFAULT_EXTENDED_IMAGE_NAME
from aicage.registry.image_selection import ImageSelection

from ._fixtures import build_run_config


class LocalBuildRunnerTests(TestCase):
    def test_run_build_invokes_docker(self) -> None:
        with mock.patch(
            "aicage.config.images_metadata.models.find_packaged_path",
            return_value=Path("/tmp/build/Dockerfile"),
        ):
            run_config = build_run_config()
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "logs" / "build.log"
            with (
                mock.patch(
                    "aicage.docker.build.find_packaged_path",
                    return_value=Path("/tmp/build/Dockerfile"),
                ),
                mock.patch(
                    "aicage.docker.build.subprocess.run",
                    return_value=mock.Mock(returncode=0),
                ) as run_mock,
            ):
                build.run_build(
                    run_config=run_config,
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    image_ref="aicage:claude-ubuntu",
                    log_path=log_path,
                )

        run_mock.assert_called_once()
        command = run_mock.call_args.args[0]
        self.assertEqual(
            [
                "docker",
                "build",
                "--no-cache",
                "--file",
                "/tmp/build/Dockerfile",
                "--build-arg",
                "BASE_IMAGE=ghcr.io/aicage/aicage-image-base:ubuntu",
                "--build-arg",
                "AGENT=claude",
                "--tag",
                "aicage:claude-ubuntu",
                "/tmp/build",
            ],
            command,
        )

    def test_run_build_raises_on_failure(self) -> None:
        with mock.patch(
            "aicage.config.images_metadata.models.find_packaged_path",
            return_value=Path("/tmp/build/Dockerfile"),
        ):
            run_config = build_run_config()
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "logs" / "build.log"
            with (
                mock.patch(
                    "aicage.docker.build.find_packaged_path",
                    return_value=Path("/tmp/build/Dockerfile"),
                ),
                mock.patch(
                    "aicage.docker.build.subprocess.run",
                    return_value=mock.Mock(returncode=1),
                ),
                self.assertRaises(DockerError),
            ):
                build.run_build(
                    run_config=run_config,
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    image_ref="aicage:claude-ubuntu",
                    log_path=log_path,
                )

    def test_run_custom_base_build_invokes_docker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "logs" / "build.log"
            dockerfile_path = Path(tmp_dir) / "Dockerfile"
            dockerfile_path.write_text("FROM ubuntu:latest\n", encoding="utf-8")
            with mock.patch(
                "aicage.docker.build.subprocess.run",
                return_value=CompletedProcess([], 0),
            ) as run_mock:
                build.run_custom_base_build(
                    dockerfile_path=dockerfile_path,
                    build_root=Path(tmp_dir),
                    from_image="ubuntu:latest",
                    image_ref="aicage:base-sample",
                    log_path=log_path,
                )

        command = run_mock.call_args.args[0]
        self.assertEqual(
            [
                "docker",
                "build",
                "--no-cache",
                "--file",
                str(dockerfile_path),
                "--build-arg",
                "FROM_IMAGE=ubuntu:latest",
                "--tag",
                "aicage:base-sample",
                str(Path(tmp_dir)),
            ],
            command,
        )

    def test_run_custom_base_build_raises_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "logs" / "build.log"
            dockerfile_path = Path(tmp_dir) / "Dockerfile"
            dockerfile_path.write_text("FROM ubuntu:latest\n", encoding="utf-8")
            with (
                mock.patch(
                    "aicage.docker.build.subprocess.run",
                    return_value=CompletedProcess([], 1),
                ),
                self.assertRaises(DockerError),
            ):
                build.run_custom_base_build(
                    dockerfile_path=dockerfile_path,
                    build_root=Path(tmp_dir),
                    from_image="ubuntu:latest",
                    image_ref="aicage:base-sample",
                    log_path=log_path,
                )

    def test_run_extended_build_builds_all_extensions(self) -> None:
        run_config = _run_config()
        extensions = [_extension("extra"), _extension("more")]
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "build.log"
            with (
                mock.patch(
                    "aicage.docker.build.find_packaged_path",
                    return_value=Path("/tmp/Dockerfile"),
                ),
                mock.patch(
                    "aicage.docker.build.subprocess.run",
                    return_value=CompletedProcess([], 0),
                ) as run_mock,
                mock.patch("aicage.docker.build._cleanup_intermediate_images") as cleanup_mock,
            ):
                build.run_extended_build(
                    run_config=run_config,
                    base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                    extensions=extensions,
                    log_path=log_path,
                )
        self.assertEqual(2, run_mock.call_count)
        cleanup_mock.assert_called_once()

    def test_run_extended_build_raises_on_failure(self) -> None:
        run_config = _run_config()
        extension = _extension("extra")
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "build.log"
            with (
                mock.patch(
                    "aicage.docker.build.find_packaged_path",
                    return_value=Path("/tmp/Dockerfile"),
                ),
                mock.patch(
                    "aicage.docker.build.subprocess.run",
                    return_value=CompletedProcess([], 1),
                ),
            ):
                with self.assertRaises(DockerError):
                    build.run_extended_build(
                        run_config=run_config,
                        base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                        extensions=[extension],
                        log_path=log_path,
                    )

    @staticmethod
    def test_cleanup_intermediate_images_logs_failures() -> None:
        logger = mock.Mock()
        with mock.patch(
            "aicage.docker.build.subprocess.run",
            return_value=CompletedProcess([], 1),
        ):
            build._cleanup_intermediate_images(["aicage:tmp"], logger)
        logger.info.assert_called_once()


def _extension(extension_id: str) -> ExtensionMetadata:
    return ExtensionMetadata(
        extension_id=extension_id,
        name=extension_id,
        description="desc",
        directory=Path("/tmp/ext"),
        scripts_dir=Path("/tmp/ext/scripts"),
        dockerfile_path=None,
    )


def _run_config() -> RunConfig:
    global_cfg = GlobalConfig(
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
    images_metadata = ImagesMetadata(
        aicage_image=_ImageReleaseInfo(version="0.3.3"),
        aicage_image_base=_ImageReleaseInfo(version="0.3.3"),
        bases={},
        agents={},
    )
    return RunConfig(
        project_path=Path("/tmp/project"),
        agent="codex",
        context=ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path="/tmp/project", agents={}),
            global_cfg=global_cfg,
            images_metadata=images_metadata,
            extensions={},
        ),
        selection=ImageSelection(
            image_ref=f"{DEFAULT_EXTENDED_IMAGE_NAME}:codex-ubuntu-extra",
            base="ubuntu",
            extensions=["extra"],
            base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
        ),
        project_docker_args="",
        mounts=[],
    )
