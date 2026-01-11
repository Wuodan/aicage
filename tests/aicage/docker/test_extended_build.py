import tempfile
from pathlib import Path
from subprocess import CompletedProcess
from unittest import TestCase, mock

from aicage.config.context import ConfigContext
from aicage.config.extensions import ExtensionMetadata
from aicage.config.global_config import GlobalConfig
from aicage.config.images_metadata.models import ImagesMetadata, _ImageReleaseInfo
from aicage.config.project_config import ProjectConfig
from aicage.config.runtime_config import RunConfig
from aicage.docker.build import (
    _cleanup_intermediate_images,
    _intermediate_image_ref,
    _parse_image_ref,
    run_extended_build,
)
from aicage.docker.errors import DockerError
from aicage.registry.image_selection import ImageSelection


class ExtendedRunnerTests(TestCase):
    def test_parse_image_ref_rejects_missing_tag(self) -> None:
        with self.assertRaises(DockerError):
            _parse_image_ref("repo")

    def test_intermediate_image_ref_includes_extension(self) -> None:
        run_config = self._run_config()
        extension = self._extension("extra")
        ref = _intermediate_image_ref(run_config, extension, 0)
        self.assertEqual("aicage-extended:tmp-codex-ubuntu-1-extra", ref)

    def test_run_extended_build_builds_all_extensions(self) -> None:
        run_config = self._run_config()
        extensions = [self._extension("extra"), self._extension("more")]
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
                run_extended_build(
                    run_config=run_config,
                    base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                    extensions=extensions,
                    log_path=log_path,
                )
        self.assertEqual(2, run_mock.call_count)
        cleanup_mock.assert_called_once()

    def test_run_extended_build_raises_on_failure(self) -> None:
        run_config = self._run_config()
        extension = self._extension("extra")
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
                    run_extended_build(
                        run_config=run_config,
                        base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                        extensions=[extension],
                        log_path=log_path,
                    )

    def test_cleanup_intermediate_images_logs_failures(self) -> None:
        logger = mock.Mock()
        with mock.patch(
            "aicage.docker.build.subprocess.run",
            return_value=CompletedProcess([], 1),
        ):
            _cleanup_intermediate_images(["aicage:tmp"], logger)
        logger.info.assert_called_once()

    @staticmethod
    def _extension(extension_id: str) -> ExtensionMetadata:
        return ExtensionMetadata(
            extension_id=extension_id,
            name=extension_id,
            description="desc",
            directory=Path("/tmp/ext"),
            scripts_dir=Path("/tmp/ext/scripts"),
            dockerfile_path=None,
        )

    @staticmethod
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
                image_ref="aicage-extended:codex-ubuntu-extra",
                base="ubuntu",
                extensions=["extra"],
                base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
            ),
            project_docker_args="",
            mounts=[],
        )
