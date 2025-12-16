from pathlib import Path
from unittest import TestCase, mock

from aicage import cli
from aicage.errors import CliError
from aicage.runtime.run_args import DockerRunArgs, assemble_docker_run


class PromptTests(TestCase):
    def test_prompt_requires_tty(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=False):
            with self.assertRaises(CliError):
                cli.prompt_for_base("codex", "ubuntu", ["ubuntu"])

    def test_prompt_validates_choice(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", return_value="fedora"):
            with self.assertRaises(CliError):
                cli.prompt_for_base("codex", "ubuntu", ["ubuntu"])

    def test_assemble_includes_workspace_mount(self) -> None:
        with mock.patch("aicage.runtime.run_args._resolve_user_ids", return_value=[]):
            run_args = DockerRunArgs(
                image_ref="wuodan/aicage:codex-ubuntu-latest",
                project_path=Path("/work/project"),
                tool_config_host=Path("/host/.codex"),
                tool_mount_container=Path("/aicage/tool-config"),
                merged_docker_args="--network=host",
                tool_args=["--flag"],
                env=["AICAGE_TOOL_PATH=~/.codex"],
            )
            cmd = assemble_docker_run(run_args)
        self.assertEqual(
            [
                "docker",
                "run",
                "--rm",
                "-it",
                "-e",
                "AICAGE_TOOL_PATH=~/.codex",
                "-v",
                "/work/project:/workspace",
                "-v",
                "/host/.codex:/aicage/tool-config",
                "--network=host",
                "wuodan/aicage:codex-ubuntu-latest",
                "--flag",
            ],
            cmd,
        )
