from pathlib import Path
from unittest import TestCase, mock

from aicage.config.project_config import AgentConfig, _AgentMounts
from aicage.paths import container_project_path
from aicage.runtime.docker_args import _git_root
from aicage.runtime.run_args import MountSpec


class GitRootTests(TestCase):
    def test_resolve_git_root_mount_skips_without_git_root(self) -> None:
        project_path = Path("/tmp/project")
        agent_cfg = AgentConfig()
        with (
            mock.patch("aicage.runtime.docker_args._git_root.resolve_git_root", return_value=None),
        ):
            mounts = _git_root.resolve_git_root_mount(project_path, agent_cfg)
        self.assertEqual([], mounts)

    def test_resolve_git_root_mount_skips_for_project_root(self) -> None:
        project_path = Path("/tmp/project")
        agent_cfg = AgentConfig()
        with (
            mock.patch("aicage.runtime.docker_args._git_root.resolve_git_root", return_value=project_path),
        ):
            mounts = _git_root.resolve_git_root_mount(project_path, agent_cfg)
        self.assertEqual([], mounts)

    def test_resolve_git_root_mount_respects_pref(self) -> None:
        project_path = Path("/tmp/project")
        git_root = Path("/tmp/root")
        agent_cfg = AgentConfig(mounts=_AgentMounts(gitroot=False))
        with mock.patch(
            "aicage.runtime.docker_args._git_root.resolve_git_root",
            return_value=git_root,
        ):
            mounts = _git_root.resolve_git_root_mount(project_path, agent_cfg)
        self.assertEqual([], mounts)

    def test_resolve_git_root_mount_uses_preference(self) -> None:
        project_path = Path("/tmp/project")
        git_root = Path("/tmp/root")
        agent_cfg = AgentConfig(mounts=_AgentMounts(gitroot=True))
        with mock.patch(
            "aicage.runtime.docker_args._git_root.resolve_git_root",
            return_value=git_root,
        ):
            mounts = _git_root.resolve_git_root_mount(project_path, agent_cfg)
        expected_mounts = [
            MountSpec(
                host_path=git_root,
                container_path=container_project_path(git_root),
            )
        ]
        self.assertEqual(expected_mounts, mounts)
