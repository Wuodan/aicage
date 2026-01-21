import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.project_config import AgentConfig
from aicage.runtime.docker_args import _git_config


class GitConfigTests(TestCase):
    def test_resolve_git_config_path_parses_first_file(self) -> None:
        output = "file:/home/user/.gitconfig user.name=Name\nfile:/tmp/other key=value\n"
        with mock.patch("aicage.runtime.docker_args._git_config.capture_stdout", return_value=output):
            path = _git_config._resolve_git_config_path()
        self.assertEqual(Path("/home/user/.gitconfig"), path)

    def test_resolve_git_config_path_handles_empty(self) -> None:
        with mock.patch("aicage.runtime.docker_args._git_config.capture_stdout", return_value=""):
            path = _git_config._resolve_git_config_path()
        self.assertIsNone(path)

    def test_resolve_git_config_mount_prompts_when_unset(self) -> None:
        agent_cfg = AgentConfig()
        with tempfile.TemporaryDirectory() as tmp_dir:
            git_config = Path(tmp_dir) / ".gitconfig"
            git_config.write_text("[user]\nname = Test\n", encoding="utf-8")
            with (
                mock.patch(
                    "aicage.runtime.docker_args._git_config._resolve_git_config_path",
                    return_value=git_config,
                ),
                mock.patch(
                    "aicage.runtime.docker_args._git_config.prompt_mount_git_config",
                    return_value=True,
                ) as prompt_mock,
            ):
                mounts = _git_config.resolve_git_config_mount(agent_cfg)

        self.assertEqual(1, len(mounts))
        self.assertEqual(git_config, mounts[0].host_path)
        prompt_mock.assert_called_once_with(git_config)

    def test_resolve_git_config_mount_persists_preference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            gitconfig = Path(tmp_dir) / ".gitconfig"
            gitconfig.write_text("user.name = coder", encoding="utf-8")
            agent_cfg = AgentConfig()

            with (
                mock.patch(
                    "aicage.runtime.docker_args._git_config._resolve_git_config_path",
                    return_value=gitconfig,
                ),
                mock.patch(
                    "aicage.runtime.docker_args._git_config.prompt_mount_git_config",
                    return_value=True,
                ),
            ):
                mounts = _git_config.resolve_git_config_mount(agent_cfg)

        self.assertTrue(agent_cfg.mounts.gitconfig)
        self.assertEqual(1, len(mounts))
