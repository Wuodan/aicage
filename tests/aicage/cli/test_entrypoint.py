import tempfile
from dataclasses import replace
from pathlib import Path
from unittest import TestCase, mock

from aicage.cli.entrypoint import main
from aicage.cli_types import ParsedArgs
from aicage.config.agent.models import AgentMetadata
from aicage.config.base.models import BaseMetadata
from aicage.config.context import ConfigContext
from aicage.config.project_config import ProjectConfig
from aicage.config.runtime_config import RunConfig
from aicage.paths import CONTAINER_AGENT_CONFIG_DIR
from aicage.registry.image_selection.models import ImageSelection
from aicage.runtime.run_args import DockerRunArgs, MountSpec


def _build_run_args(
    project_path: Path, image_ref: str, merged_docker_args: str, agent_args: list[str]
) -> DockerRunArgs:
    return DockerRunArgs(
        image_ref=image_ref,
        project_path=project_path,
        agent_config_mounts=[
            MountSpec(
                host_path=project_path / ".codex",
                container_path=CONTAINER_AGENT_CONFIG_DIR / ".codex",
            )
        ],
        merged_docker_args=merged_docker_args,
        agent_args=agent_args,
    )


def _build_run_config(project_path: Path, image_ref: str) -> RunConfig:
    bases, agents = _build_agents_and_bases()
    return RunConfig(
        project_path=project_path,
        agent="codex",
        context=ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path=str(project_path), agents={}),
            agents=agents,
            bases=bases,
            extensions={},
        ),
        selection=ImageSelection(
            image_ref=image_ref,
            base="ubuntu",
            extensions=[],
            base_image_ref=image_ref,
        ),
        project_docker_args="--project",
        mounts=[],
        env=[],
    )


def _build_agents_and_bases(
) -> tuple[dict[str, BaseMetadata], dict[str, AgentMetadata]]:
    bases = {
        "alpine": BaseMetadata(
            from_image="alpine:latest",
            base_image_distro="Alpine",
            base_image_description="Minimal",
            build_local=False,
            local_definition_dir=Path("/tmp/alpine"),
        ),
        "debian": BaseMetadata(
            from_image="debian:latest",
            base_image_distro="Debian",
            base_image_description="Default",
            build_local=False,
            local_definition_dir=Path("/tmp/debian"),
        ),
        "ubuntu": BaseMetadata(
            from_image="ubuntu:latest",
            base_image_distro="Ubuntu",
            base_image_description="Default",
            build_local=False,
            local_definition_dir=Path("/tmp/ubuntu"),
        ),
    }
    agents = {
        "codex": AgentMetadata(
            agent_path=["~/.codex"],
            agent_full_name="Codex CLI",
            agent_homepage="https://example.com",
            build_local=False,
            valid_bases={
                "alpine": "ghcr.io/aicage/aicage:codex-alpine",
                "debian": "ghcr.io/aicage/aicage:codex-debian",
                "ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu",
            },
            local_definition_dir=Path("/tmp/codex"),
        )
    }
    return bases, agents


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
            exit_code = main([])

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
                mock.patch("aicage.cli.entrypoint.ensure_image"),
                mock.patch("aicage.cli.entrypoint.build_run_args", return_value=run_args),
                mock.patch("aicage.cli.entrypoint.run_container") as run_mock,
            ):
                exit_code = main([])

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
                mock.patch("aicage.cli.entrypoint.ensure_image"),
                mock.patch("aicage.cli.entrypoint.build_run_args", return_value=run_args),
                mock.patch("aicage.cli.entrypoint.run_container"),
            ):
                exit_code = main([])

            self.assertEqual(0, exit_code)

    def test_main_rejects_project_path_at_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home_path = Path(tmp_dir)
            run_config = _build_run_config(
                home_path,
                "ghcr.io/aicage/aicage:codex-debian",
            )
            with (
                mock.patch(
                    "aicage.cli.entrypoint.parse_cli",
                    return_value=ParsedArgs(
                        False,
                        "--cli",
                        "codex",
                        ["--flag"],
                        None,
                        False,
                        None,
                    ),
                ),
                mock.patch("aicage.cli.entrypoint.Path.home", return_value=home_path),
                mock.patch("aicage.cli.entrypoint.load_run_config", return_value=run_config),
                mock.patch("aicage.cli.entrypoint.ensure_image") as ensure_mock,
                mock.patch("aicage.cli.entrypoint.build_run_args") as build_mock,
                mock.patch("aicage.cli.entrypoint.run_container") as run_mock,
            ):
                exit_code = main([])

            self.assertEqual(1, exit_code)
            ensure_mock.assert_not_called()
            build_mock.assert_not_called()
            run_mock.assert_not_called()

    def test_main_rejects_mount_at_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()
            home_path = Path(tmp_dir) / "home"
            home_path.mkdir()
            run_config = _build_run_config(
                project_path,
                "ghcr.io/aicage/aicage:codex-debian",
            )
            run_config = replace(
                run_config,
                mounts=[
                    MountSpec(
                        host_path=home_path,
                        container_path=CONTAINER_AGENT_CONFIG_DIR / ".home",
                    )
                ],
            )
            with (
                mock.patch(
                    "aicage.cli.entrypoint.parse_cli",
                    return_value=ParsedArgs(
                        False,
                        "--cli",
                        "codex",
                        ["--flag"],
                        None,
                        False,
                        None,
                    ),
                ),
                mock.patch("aicage.cli.entrypoint.Path.home", return_value=home_path),
                mock.patch("aicage.cli.entrypoint.load_run_config", return_value=run_config),
                mock.patch("aicage.cli.entrypoint.ensure_image") as ensure_mock,
                mock.patch("aicage.cli.entrypoint.build_run_args") as build_mock,
                mock.patch("aicage.cli.entrypoint.run_container") as run_mock,
            ):
                exit_code = main([])

            self.assertEqual(1, exit_code)
            ensure_mock.assert_not_called()
            build_mock.assert_not_called()
            run_mock.assert_not_called()
