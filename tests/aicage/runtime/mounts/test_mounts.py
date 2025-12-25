import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.runtime.mounts import _auth as auth_mounts


class AuthMountTests(TestCase):
    def test_mount_preferences_round_trip(self) -> None:
        prefs = auth_mounts._MountPreferences.from_mapping({"gitconfig": True, "gnupg": False, "ssh": True})
        self.assertTrue(prefs.gitconfig)
        self.assertFalse(prefs.gnupg)
        self.assertTrue(prefs.ssh)
        self.assertEqual({"gitconfig": True, "gnupg": False, "ssh": True}, prefs.to_mapping())

    def test_store_mount_preferences_updates_tool_config(self) -> None:
        tool_cfg = {"mounts": {"gitconfig": False}}
        prefs = auth_mounts._MountPreferences(gitconfig=True, gnupg=True)
        auth_mounts._store_mount_preferences(tool_cfg, prefs)
        self.assertEqual({"gitconfig": True, "gnupg": True}, tool_cfg["mounts"])

    def test_load_mount_preferences_defaults_missing(self) -> None:
        prefs = auth_mounts._load_mount_preferences({})
        self.assertIsNone(prefs.gitconfig)
        self.assertIsNone(prefs.gnupg)
        self.assertIsNone(prefs.ssh)

    def test_build_auth_mounts_collects_git_and_gpg(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            gitconfig = home / ".gitconfig"
            gitconfig.write_text("user.name = coder", encoding="utf-8")
            gnupg = home / ".gnupg"
            gnupg.mkdir()

            prefs = auth_mounts._MountPreferences()
            with mock.patch("pathlib.Path.home", return_value=home), mock.patch(
                "aicage.runtime.mounts._auth.resolve_git_config_path", return_value=gitconfig
            ), mock.patch("aicage.runtime.mounts._auth.is_commit_signing_enabled", return_value=True), mock.patch(
                "aicage.runtime.mounts._auth.resolve_signing_format", return_value=None
            ), mock.patch(
                "aicage.runtime.mounts._auth.resolve_gpg_home", return_value=gnupg
            ), mock.patch(
                "aicage.runtime.mounts._auth.prompt_yes_no", return_value=True
            ):
                mounts, updated = auth_mounts._build_auth_mounts(Path("/repo"), prefs)

        self.assertTrue(updated)
        self.assertEqual({gitconfig, gnupg}, {mount.host_path for mount in mounts})

    def test_build_auth_mounts_uses_existing_ssh_preference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            ssh_dir = home / ".ssh"
            ssh_dir.mkdir()

            prefs = auth_mounts._MountPreferences(ssh=True)
            with mock.patch("pathlib.Path.home", return_value=home), mock.patch(
                "aicage.runtime.mounts._auth.resolve_git_config_path", return_value=None
            ), mock.patch("aicage.runtime.mounts._auth.is_commit_signing_enabled", return_value=True), mock.patch(
                "aicage.runtime.mounts._auth.resolve_signing_format", return_value="ssh"
            ), mock.patch(
                "aicage.runtime.mounts._auth.prompt_yes_no"
            ) as prompt_mock:
                mounts, updated = auth_mounts._build_auth_mounts(Path("/repo"), prefs)

        prompt_mock.assert_not_called()
        self.assertFalse(updated)
        self.assertEqual(ssh_dir, mounts[0].host_path)

    def test_build_auth_mounts_uses_gpg_prefs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            gpg_home = Path(tmp_dir) / ".gnupg"
            gpg_home.mkdir()

            prefs = auth_mounts._MountPreferences(gnupg=True)
            with (
                mock.patch("aicage.runtime.mounts._auth.resolve_git_config_path", return_value=None),
                mock.patch("aicage.runtime.mounts._auth.is_commit_signing_enabled", return_value=True),
                mock.patch("aicage.runtime.mounts._auth.resolve_signing_format", return_value=None),
                mock.patch("aicage.runtime.mounts._auth.resolve_gpg_home", return_value=gpg_home),
                mock.patch("aicage.runtime.mounts._auth.prompt_yes_no") as prompt_mock,
            ):
                mounts, updated = auth_mounts._build_auth_mounts(Path("/repo"), prefs)

        prompt_mock.assert_not_called()
        self.assertFalse(updated)
        self.assertEqual(1, len(mounts))
        self.assertEqual(gpg_home, mounts[0].host_path)

    def test_build_auth_mounts_prompts_for_ssh(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            ssh_dir = Path(tmp_dir) / ".ssh"
            ssh_dir.mkdir()

            prefs = auth_mounts._MountPreferences()
            with (
                mock.patch("aicage.runtime.mounts._auth.resolve_git_config_path", return_value=None),
                mock.patch("aicage.runtime.mounts._auth.is_commit_signing_enabled", return_value=True),
                mock.patch("aicage.runtime.mounts._auth.resolve_signing_format", return_value="ssh"),
                mock.patch("aicage.runtime.mounts._auth.default_ssh_dir", return_value=ssh_dir),
                mock.patch("aicage.runtime.mounts._auth.prompt_yes_no", return_value=True),
            ):
                mounts, updated = auth_mounts._build_auth_mounts(Path("/repo"), prefs)

        self.assertTrue(updated)
        self.assertTrue(prefs.ssh)
        self.assertEqual(1, len(mounts))
        self.assertEqual(ssh_dir, mounts[0].host_path)
