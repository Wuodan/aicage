from pathlib import Path
from unittest import TestCase, mock

from aicage.config.project_config import AgentConfig, _AgentMounts
from aicage.paths import container_project_path
from aicage.runtime.docker_args import _git_root
from aicage.runtime.run_args import MountSpec


class GitRootTests(TestCase):
    def test__resolve_git_root_prefers_superproject(self) -> None:
        project_path = Path("/tmp/project")
        superproject = "/tmp/root"
        with mock.patch(
            "aicage.runtime.docker_args._git_root.capture_stdout",
            return_value=f"{superproject}\n",
        ) as capture_mock:
            result = _git_root._resolve_git_root(project_path)
        self.assertEqual(Path(superproject).resolve(), result)
        capture_mock.assert_called_once_with(
            ["git", "rev-parse", "--show-superproject-working-tree"],
            cwd=project_path,
        )

    def test__resolve_git_root_falls_back_to_toplevel(self) -> None:
        project_path = Path("/tmp/project")
        toplevel = "/tmp/root"
        with mock.patch(
            "aicage.runtime.docker_args._git_root.capture_stdout",
            side_effect=["", f"{toplevel}\n"],
        ) as capture_mock:
            result = _git_root._resolve_git_root(project_path)
        self.assertEqual(Path(toplevel).resolve(), result)
        self.assertEqual(2, capture_mock.call_count)

    def test_resolve_git_root_mount_skips_without_git_root(self) -> None:
        project_path = Path("/tmp/project")
        agent_cfg = AgentConfig()
        with (
            mock.patch("aicage.runtime.docker_args._git_root._resolve_git_root", return_value=None),
            mock.patch("aicage.runtime.docker_args._git_root.prompt_mount_git_root") as prompt_mock,
        ):
            mounts = _git_root.resolve_git_root_mount(project_path, agent_cfg)
        self.assertEqual([], mounts)
        prompt_mock.assert_not_called()

    def test_resolve_git_root_mount_skips_for_project_root(self) -> None:
        project_path = Path("/tmp/project")
        agent_cfg = AgentConfig()
        with (
            mock.patch("aicage.runtime.docker_args._git_root._resolve_git_root", return_value=project_path),
            mock.patch("aicage.runtime.docker_args._git_root.prompt_mount_git_root") as prompt_mock,
        ):
            mounts = _git_root.resolve_git_root_mount(project_path, agent_cfg)
        self.assertEqual([], mounts)
        prompt_mock.assert_not_called()

    def test_resolve_git_root_mount_prompts_and_persists(self) -> None:
        project_path = Path("/tmp/project")
        git_root = Path("/tmp/root")
        agent_cfg = AgentConfig(mounts=_AgentMounts())
        with mock.patch(
            "aicage.runtime.docker_args._git_root._resolve_git_root",
            return_value=git_root,
        ), mock.patch(
            "aicage.runtime.docker_args._git_root.prompt_mount_git_root",
            return_value=True,
        ) as prompt_mock:
            mounts = _git_root.resolve_git_root_mount(project_path, agent_cfg)
        expected_mounts = [
            MountSpec(
                host_path=git_root,
                container_path=container_project_path(git_root),
            )
        ]
        self.assertEqual(expected_mounts, mounts)
        self.assertTrue(agent_cfg.mounts.gitroot)
        prompt_mock.assert_called_once_with(project_path, git_root)

    def test_resolve_git_root_mount_respects_pref(self) -> None:
        project_path = Path("/tmp/project")
        git_root = Path("/tmp/root")
        agent_cfg = AgentConfig(mounts=_AgentMounts(gitroot=False))
        with (
            mock.patch("aicage.runtime.docker_args._git_root._resolve_git_root", return_value=git_root),
            mock.patch("aicage.runtime.docker_args._git_root.prompt_mount_git_root") as prompt_mock,
        ):
            mounts = _git_root.resolve_git_root_mount(project_path, agent_cfg)
        self.assertEqual([], mounts)
        prompt_mock.assert_not_called()
