import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.project_config import AgentConfig, _AgentMounts
from aicage.runtime.docker_args import _ssh_keys


class SshKeyTests(TestCase):
    def test_resolve_ssh_mount_skips_when_signing_disabled(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(ssh=True))
        with mock.patch(
            "aicage.runtime.docker_args._ssh_keys.is_commit_signing_enabled",
            return_value=False,
        ):
            mounts = _ssh_keys.resolve_ssh_mount(Path("/repo"), agent_cfg)
        self.assertEqual([], mounts)

    def test_resolve_ssh_mount_skips_for_non_ssh_format(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(ssh=True))
        with (
            mock.patch(
                "aicage.runtime.docker_args._ssh_keys.is_commit_signing_enabled",
                return_value=True,
            ),
            mock.patch(
                "aicage.runtime.docker_args._ssh_keys.resolve_signing_format",
                return_value="gpg",
            ),
        ):
            mounts = _ssh_keys.resolve_ssh_mount(Path("/repo"), agent_cfg)
        self.assertEqual([], mounts)

    def test_resolve_ssh_mount_respects_pref(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(ssh=False))
        ssh_dir = Path("/tmp/ssh")
        with (
            mock.patch("aicage.runtime.docker_args._ssh_keys.is_commit_signing_enabled", return_value=True),
            mock.patch("aicage.runtime.docker_args._ssh_keys.resolve_signing_format", return_value="ssh"),
            mock.patch("aicage.runtime.docker_args._ssh_keys.resolve_ssh_dir", return_value=ssh_dir),
        ):
            mounts = _ssh_keys.resolve_ssh_mount(Path("/repo"), agent_cfg)
        self.assertEqual([], mounts)

    def test_resolve_ssh_mount_uses_preference(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(ssh=True))
        with tempfile.TemporaryDirectory() as tmp_dir:
            ssh_dir = Path(tmp_dir) / "ssh"
            ssh_dir.mkdir()
            with (
                mock.patch("aicage.runtime.docker_args._ssh_keys.is_commit_signing_enabled", return_value=True),
                mock.patch("aicage.runtime.docker_args._ssh_keys.resolve_signing_format", return_value="ssh"),
                mock.patch("aicage.runtime.docker_args._ssh_keys.resolve_ssh_dir", return_value=ssh_dir),
            ):
                mounts = _ssh_keys.resolve_ssh_mount(Path("/repo"), agent_cfg)
        self.assertEqual(1, len(mounts))
        self.assertEqual(ssh_dir, mounts[0].host_path)
