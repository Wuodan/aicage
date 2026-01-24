import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.project_config import AgentConfig, _AgentMounts
from aicage.runtime.docker_args import _gpg


class GpgHomeTests(TestCase):
    def test_resolve_gpg_mount_skips_when_signing_disabled(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(gnupg=True))
        with mock.patch(
            "aicage.runtime.docker_args._gpg.is_commit_signing_enabled",
            return_value=False,
        ):
            mounts = _gpg.resolve_gpg_mount(Path("/tmp/project"), agent_cfg)
        self.assertEqual([], mounts)

    def test_resolve_gpg_mount_skips_for_ssh_format(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(gnupg=True))
        with (
            mock.patch(
                "aicage.runtime.docker_args._gpg.is_commit_signing_enabled",
                return_value=True,
            ),
            mock.patch(
                "aicage.runtime.docker_args._gpg.resolve_signing_format",
                return_value="ssh",
            ),
        ):
            mounts = _gpg.resolve_gpg_mount(Path("/tmp/project"), agent_cfg)
        self.assertEqual([], mounts)

    def test_resolve_gpg_mount_respects_pref(self) -> None:
        gpg_home = Path("/tmp/gpg")
        agent_cfg = AgentConfig(mounts=_AgentMounts(gnupg=False))
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
                "aicage.runtime.docker_args._gpg.resolve_gpg_home",
                return_value=gpg_home,
            ),
        ):
            mounts = _gpg.resolve_gpg_mount(Path("/tmp/project"), agent_cfg)
        self.assertEqual([], mounts)

    def test_resolve_gpg_mount_uses_preference(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(gnupg=True))
        with tempfile.TemporaryDirectory() as tmp_dir:
            gpg_home = Path(tmp_dir) / "gnupg"
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
                    "aicage.runtime.docker_args._gpg.resolve_gpg_home",
                    return_value=gpg_home,
                ),
            ):
                mounts = _gpg.resolve_gpg_mount(Path("/tmp/project"), agent_cfg)
        self.assertEqual(1, len(mounts))
        self.assertEqual(gpg_home, mounts[0].host_path)
