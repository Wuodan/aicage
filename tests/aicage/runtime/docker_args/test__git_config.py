import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.project_config import AgentConfig
from aicage.runtime.docker_args import _git_config


class GitConfigTests(TestCase):
    def test_resolve_git_config_mount_skips_without_config(self) -> None:
        agent_cfg = AgentConfig()
        with mock.patch(
            "aicage.runtime.docker_args._git_config.resolve_git_config_path",
            return_value=None,
        ):
            mounts = _git_config.resolve_git_config_mount(agent_cfg)
        self.assertEqual([], mounts)

    def test_resolve_git_config_mount_respects_pref(self) -> None:
        agent_cfg = AgentConfig()
        agent_cfg.mounts.gitconfig = True
        with tempfile.TemporaryDirectory() as tmp_dir:
            gitconfig = Path(tmp_dir) / ".gitconfig"
            gitconfig.write_text("user.name = tester", encoding="utf-8")
            with mock.patch(
                "aicage.runtime.docker_args._git_config.resolve_git_config_path",
                return_value=gitconfig,
            ):
                mounts = _git_config.resolve_git_config_mount(agent_cfg)
        self.assertEqual(1, len(mounts))
        self.assertEqual(gitconfig, mounts[0].host_path)
