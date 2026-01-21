import os
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.project_config import AgentConfig, _AgentMounts
from aicage.runtime.docker_args import _gpg


class GpgHomeTests(TestCase):
    def test_resolve_gpg_home_parses_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            gpg_home = Path(tmp_dir) / ".gnupg"
            gpg_home.mkdir()
            with mock.patch(
                "aicage.runtime.docker_args._gpg.capture_stdout",
                return_value=f"{gpg_home}\n",
            ):
                path = _gpg._resolve_gpg_home()
        self.assertEqual(gpg_home, path)

    def test_resolve_gpg_home_falls_back_to_home_gnupg(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            gpg_home = Path(tmp_dir) / ".gnupg"
            gpg_home.mkdir()
            with (
                mock.patch.dict(
                    os.environ,
                    {"HOME": tmp_dir, "USERPROFILE": tmp_dir},
                    clear=False,
                ),
                mock.patch("aicage.runtime.docker_args._gpg.capture_stdout", return_value=""),
            ):
                path = _gpg._resolve_gpg_home()
        self.assertEqual(gpg_home, path)

    def test_resolve_gpg_home_handles_missing_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            with (
                mock.patch.dict(
                    os.environ,
                    {"HOME": tmp_dir, "USERPROFILE": tmp_dir},
                    clear=False,
                ),
                mock.patch(
                    "aicage.runtime.docker_args._gpg.capture_stdout",
                    return_value="",
                ),
            ):
                path = _gpg._resolve_gpg_home()
        self.assertIsNone(path)

    def test_resolve_gpg_mount_prompts_when_unset(self) -> None:
        agent_cfg = AgentConfig()
        with tempfile.TemporaryDirectory() as tmp_dir:
            gpg_home = Path(tmp_dir) / ".gnupg"
            gpg_home.mkdir()
            with (
                mock.patch(
                    "aicage.runtime.docker_args._gpg.is_commit_signing_enabled",
                    return_value=True,
                ),
                mock.patch(
                    "aicage.runtime.docker_args._gpg.resolve_signing_format",
                    return_value="gpg",
                ),
                mock.patch(
                    "aicage.runtime.docker_args._gpg._resolve_gpg_home",
                    return_value=gpg_home,
                ),
                mock.patch(
                    "aicage.runtime.docker_args._gpg.prompt_mount_gpg_keys",
                    return_value=True,
                ) as prompt_mock,
            ):
                mounts = _gpg.resolve_gpg_mount(Path("/tmp/project"), agent_cfg)

        self.assertEqual(1, len(mounts))
        self.assertEqual(gpg_home, mounts[0].host_path)
        prompt_mock.assert_called_once_with(gpg_home)

    def test_resolve_gpg_mount_uses_existing_preference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            gpg_home = Path(tmp_dir) / ".gnupg"
            gpg_home.mkdir()
            agent_cfg = AgentConfig(mounts=_AgentMounts(gnupg=True))

            with (
                mock.patch(
                    "aicage.runtime.docker_args._gpg.is_commit_signing_enabled",
                    return_value=True,
                ),
                mock.patch(
                    "aicage.runtime.docker_args._gpg.resolve_signing_format",
                    return_value=None,
                ),
                mock.patch(
                    "aicage.runtime.docker_args._gpg._resolve_gpg_home",
                    return_value=gpg_home,
                ),
                mock.patch(
                    "aicage.runtime.docker_args._gpg.prompt_mount_gpg_keys"
                ) as prompt_mock,
            ):
                mounts = _gpg.resolve_gpg_mount(Path("/repo"), agent_cfg)

        prompt_mock.assert_not_called()
        self.assertEqual(1, len(mounts))
        self.assertEqual(gpg_home, mounts[0].host_path)
