import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage import cli
from aicage.cli_types import ParsedArgs
from aicage.config.global_config import GlobalConfig
from aicage.config.runtime_config import RunConfig
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
from aicage.runtime.run_args import DockerRunArgs


def _build_run_args(
    project_path: Path, image_ref: str, merged_docker_args: str, agent_args: list[str]
) -> DockerRunArgs:
    return DockerRunArgs(
        image_ref=image_ref,
        project_path=project_path,
        agent_config_host=project_path / ".codex",
        agent_config_mount_container=Path("/aicage/agent-config"),
        merged_docker_args=merged_docker_args,
        agent_args=agent_args,
        agent_path=str(project_path / ".codex"),
    )


def _build_run_config(project_path: Path, image_ref: str) -> RunConfig:
    return RunConfig(
        project_path=project_path,
        agent="codex",
        base="ubuntu",
        image_ref=image_ref,
        base_image_ref=image_ref,
        extensions=[],
        agent_version=None,
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
        images_metadata=_build_images_metadata(),
        project_docker_args="--project",
        mounts=[],
    )


def _build_images_metadata() -> ImagesMetadata:
    return ImagesMetadata.from_mapping(
        {
            _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
            _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
            _BASES_KEY: {
                "alpine": {
                    _ROOT_IMAGE_KEY: "alpine:latest",
                    _BASE_IMAGE_DISTRO_KEY: "Alpine",
                    _BASE_IMAGE_DESCRIPTION_KEY: "Minimal",
                    _OS_INSTALLER_KEY: "distro/alpine/install.sh",
                    _TEST_SUITE_KEY: "default",
                },
                "debian": {
                    _ROOT_IMAGE_KEY: "debian:latest",
                    _BASE_IMAGE_DISTRO_KEY: "Debian",
                    _BASE_IMAGE_DESCRIPTION_KEY: "Default",
                    _OS_INSTALLER_KEY: "distro/debian/install.sh",
                    _TEST_SUITE_KEY: "default",
                },
                "ubuntu": {
                    _ROOT_IMAGE_KEY: "ubuntu:latest",
                    _BASE_IMAGE_DISTRO_KEY: "Ubuntu",
                    _BASE_IMAGE_DESCRIPTION_KEY: "Default",
                    _OS_INSTALLER_KEY: "distro/debian/install.sh",
                    _TEST_SUITE_KEY: "default",
                },
            },
            _AGENT_KEY: {
                "codex": {
                    AGENT_PATH_KEY: "~/.codex",
                    AGENT_FULL_NAME_KEY: "Codex CLI",
                    AGENT_HOMEPAGE_KEY: "https://example.com",
                    BUILD_LOCAL_KEY: False,
                    _VALID_BASES_KEY: {
                        "alpine": "ghcr.io/aicage/aicage:codex-alpine",
                        "debian": "ghcr.io/aicage/aicage:codex-debian",
                        "ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu",
                    },
                }
            },
        }
    )


class EntrypointTests(TestCase):
    def test_main_config_print(self) -> None:
        with (
            mock.patch(
                "aicage.cli.entrypoint.parse_cli",
                return_value=ParsedArgs(False, "", "", [], None, False, "print"),
            ),
            mock.patch("aicage.cli.entrypoint.print_project_config") as print_mock,
            mock.patch("aicage.cli.entrypoint.load_run_config") as load_mock,
        ):
            exit_code = cli.main([])

        self.assertEqual(0, exit_code)
        print_mock.assert_called_once()
        load_mock.assert_not_called()

    def test_main_uses_project_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir)
            run_config = _build_run_config(
                project_path,
                "ghcr.io/aicage/aicage:codex-debian",
            )
            run_args = _build_run_args(
                project_path,
                "ghcr.io/aicage/aicage:codex-debian",
                "--project --cli",
                ["--flag"],
            )
            with (
                mock.patch(
                    "aicage.cli.entrypoint.parse_cli",
                    return_value=ParsedArgs(False, "--cli", "codex", ["--flag"], None, False, None),
                ),
                mock.patch("aicage.cli.entrypoint.load_run_config", return_value=run_config),
                mock.patch("aicage.cli.entrypoint.pull_image"),
                mock.patch("aicage.cli.entrypoint.build_run_args", return_value=run_args),
                mock.patch("aicage.cli.entrypoint.run_container") as run_mock,
            ):
                exit_code = cli.main([])

            self.assertEqual(0, exit_code)
            run_mock.assert_called_once_with(run_args)

    def test_main_prompts_and_saves_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir)
            run_config = _build_run_config(
                project_path,
                "ghcr.io/aicage/aicage:codex-alpine",
            )
            run_args = _build_run_args(
                project_path,
                "ghcr.io/aicage/aicage:codex-alpine",
                "--project --cli",
                ["--flag"],
            )
            with (
                mock.patch(
                    "aicage.cli.entrypoint.parse_cli",
                    return_value=ParsedArgs(False, "--cli", "codex", ["--flag"], None, False, None),
                ),
                mock.patch("aicage.cli.entrypoint.load_run_config", return_value=run_config),
                mock.patch("aicage.cli.entrypoint.pull_image"),
                mock.patch("aicage.cli.entrypoint.build_run_args", return_value=run_args),
                mock.patch("aicage.cli.entrypoint.run_container"),
            ):
                exit_code = cli.main([])

            self.assertEqual(0, exit_code)
