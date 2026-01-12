import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.project_config import AgentConfig
from aicage.runtime.mounts import _gpg


class GpgHomeTests(TestCase):
    def test_resolve_gpg_home_parses_output(self) -> None:
        with mock.patch("aicage.runtime.mounts._gpg.capture_stdout", return_value="/home/user/.gnupg\n"):
            path = _gpg._resolve_gpg_home()
        self.assertEqual(Path("/home/user/.gnupg"), path)

    def test_resolve_gpg_home_handles_empty(self) -> None:
        with mock.patch("aicage.runtime.mounts._gpg.capture_stdout", return_value=""):
            path = _gpg._resolve_gpg_home()
        self.assertIsNone(path)

    def test_resolve_gpg_mount_prompts_when_unset(self) -> None:
        agent_cfg = AgentConfig()
        with tempfile.TemporaryDirectory() as tmp_dir:
            gpg_home = Path(tmp_dir) / ".gnupg"
            gpg_home.mkdir()
            with (
                mock.patch(
                    "aicage.runtime.mounts._gpg.is_commit_signing_enabled",
                    return_value=True,
                ),
                mock.patch(
                    "aicage.runtime.mounts._gpg.resolve_signing_format",
                    return_value="gpg",
                ),
                mock.patch(
                    "aicage.runtime.mounts._gpg._resolve_gpg_home",
                    return_value=gpg_home,
                ),
                mock.patch(
                    "aicage.runtime.mounts._gpg.prompt_mount_gpg_keys",
                    return_value=True,
                ) as prompt_mock,
            ):
                mounts = _gpg.resolve_gpg_mount(Path("/tmp/project"), agent_cfg)

        self.assertEqual(1, len(mounts))
        self.assertEqual(gpg_home, mounts[0].host_path)
        prompt_mock.assert_called_once_with(gpg_home)
