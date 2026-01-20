import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.project_config import AgentConfig, _AgentMounts
from aicage.runtime.mounts import _ssh_keys


class SshKeyTests(TestCase):
    def test_default_ssh_dir_uses_home(self) -> None:
        with mock.patch("aicage.runtime.mounts._ssh_keys.HOST_SSH_DIR", Path("/home/user/.ssh")):
            path = _ssh_keys._default_ssh_dir()
        self.assertEqual(Path("/home/user/.ssh"), path)

    def test_resolve_ssh_mount_prompts_when_preference_missing(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts())
        with tempfile.TemporaryDirectory() as tmp_dir:
            ssh_dir = Path(tmp_dir) / ".ssh"
            ssh_dir.mkdir()

            with (
                mock.patch("aicage.runtime.mounts._ssh_keys.is_commit_signing_enabled", return_value=True),
                mock.patch("aicage.runtime.mounts._ssh_keys.resolve_signing_format", return_value="ssh"),
                mock.patch("aicage.runtime.mounts._ssh_keys.HOST_SSH_DIR", ssh_dir),
                mock.patch(
                    "aicage.runtime.mounts._ssh_keys.prompt_mount_ssh_keys",
                    return_value=False,
                ) as prompt_mock,
            ):
                mounts = _ssh_keys.resolve_ssh_mount(Path("/repo"), agent_cfg)

        prompt_mock.assert_called_once()
        self.assertEqual([], mounts)
        self.assertFalse(agent_cfg.mounts.ssh)
