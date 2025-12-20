import io
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage import cli
from aicage.config import GlobalConfig, ProjectConfig
from aicage.config.context import ConfigContext
from aicage.errors import CliError
from aicage.runtime.run_args import DockerRunArgs


class FakeStore:
    def __init__(self, global_cfg: GlobalConfig, project_cfg: ProjectConfig) -> None:
        self._global_cfg = global_cfg
        self._project_cfg = project_cfg
        self.saved = None

    def load_global(self) -> GlobalConfig:
        return self._global_cfg

    def load_project(self, project_realpath: Path) -> ProjectConfig:
        self.loaded_path = project_realpath
        return self._project_cfg

    def save_project(self, project_realpath: Path, config: ProjectConfig) -> None:
        self.saved = (project_realpath, config)


def _build_context(project_path: Path, global_cfg: GlobalConfig, project_cfg: ProjectConfig) -> ConfigContext:
    store = FakeStore(global_cfg, project_cfg)
    return ConfigContext(
        store=store,
        project_path=project_path,
        project_cfg=project_cfg,
        global_cfg=global_cfg,
    )


def _build_run_args(project_path: Path, image_ref: str, merged_docker_args: str, tool_args: list[str]) -> DockerRunArgs:
    return DockerRunArgs(
        image_ref=image_ref,
        project_path=project_path,
        tool_config_host=project_path / ".codex",
        tool_mount_container=Path("/aicage/tool-config"),
        merged_docker_args=merged_docker_args,
        tool_args=tool_args,
        tool_path=str(project_path / ".codex"),
    )


def _build_global_cfg(docker_args: str, tools: dict[str, dict[str, object]] | None = None) -> GlobalConfig:
    return GlobalConfig(
        image_registry="ghcr.io",
        image_registry_api_url="https://ghcr.io/v2",
        image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
        image_repository="aicage/aicage",
        default_image_base="ubuntu",
        docker_args=docker_args,
        tools=tools or {},
    )


class MainFlowTests(TestCase):
    def test_main_uses_project_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir)
            global_cfg = _build_global_cfg("--global", tools={"codex": {"base": "fedora"}})
            project_cfg = ProjectConfig(
                path=str(project_path),
                tools={"codex": {"base": "debian", "docker_args": "--project"}},
            )

            context = _build_context(project_path, global_cfg, project_cfg)
            run_args = _build_run_args(
                project_path,
                "ghcr.io/aicage/aicage:codex-debian-latest",
                "--global --project --cli",
                ["--flag"],
            )
            with (
                mock.patch("aicage.cli.parse_cli", return_value=cli.ParsedArgs(False, "--cli", "codex", ["--flag"])),
                mock.patch("aicage.cli.build_config_context", return_value=context),
                mock.patch("aicage.cli.build_run_args", return_value=run_args),
                mock.patch(
                    "aicage.cli.assemble_docker_run",
                    return_value=["docker", "run", "--flag"],
                ) as assemble_mock,
                mock.patch("aicage.cli.subprocess.run") as run_mock,
            ):
                exit_code = cli.main([])

            self.assertEqual(0, exit_code)
            assemble_mock.assert_called_once()
            run_mock.assert_called_once_with(["docker", "run", "--flag"], check=True)

    def test_main_prompts_and_saves_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir)
            global_cfg = _build_global_cfg("--global")
            project_cfg = ProjectConfig(
                path=str(project_path), tools={"codex": {"base": "alpine", "docker_args": "--project"}}
            )

            context = _build_context(project_path, global_cfg, project_cfg)
            run_args = _build_run_args(
                project_path,
                "ghcr.io/aicage/aicage:codex-alpine-latest",
                "--global --project --cli",
                ["--flag"],
            )
            with (
                mock.patch("aicage.cli.parse_cli", return_value=cli.ParsedArgs(True, "--cli", "codex", ["--flag"])),
                mock.patch("aicage.cli.build_config_context", return_value=context),
                mock.patch("aicage.cli.build_run_args", return_value=run_args),
                mock.patch("aicage.cli.assemble_docker_run", return_value=["docker", "run", "cmd"]),
                mock.patch("sys.stderr", new_callable=io.StringIO) as stderr,
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                exit_code = cli.main([])

            self.assertEqual(0, exit_code)
            self.assertIn("docker run cmd", stdout.getvalue())
            self.assertIsNone(context.store.saved)
            self.assertEqual("", stderr.getvalue())

    def test_main_handles_no_available_bases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir)
            global_cfg = _build_global_cfg("")
            project_cfg = ProjectConfig(path=str(project_path), tools={})

            context = _build_context(project_path, global_cfg, project_cfg)
            with (
                mock.patch("aicage.cli.parse_cli", return_value=cli.ParsedArgs(True, "", "codex", [])),
                mock.patch("aicage.cli.build_config_context", return_value=context),
                mock.patch("aicage.cli.build_run_args", side_effect=CliError("No base images found")),
                mock.patch("sys.stderr", new_callable=io.StringIO) as stderr,
            ):
                exit_code = cli.main([])

            self.assertEqual(1, exit_code)
            self.assertIn("No base images found", stderr.getvalue())

    def test_main_keyboard_interrupt(self) -> None:
        with mock.patch("aicage.cli.parse_cli", side_effect=KeyboardInterrupt):
            with mock.patch("sys.stdout", new_callable=io.StringIO):
                exit_code = cli.main([])
        self.assertEqual(130, exit_code)
