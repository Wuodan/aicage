import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.errors import CliError
from aicage.runtime.extra_mounts import (
    _build_extra_mounts,
    _ExtraMountPreferences,
    _load_extra_mount_preferences,
    _resolve_entrypoint_path,
    _store_extra_mount_preferences,
    _validate_entrypoint_path,
)


class ExtraMountsTests(TestCase):
    def test_load_and_store_preferences(self) -> None:
        prefs = _load_extra_mount_preferences({"mounts": {"docker": True}, "entrypoint": "/bin/sh"})
        self.assertTrue(prefs.docker_socket)
        self.assertEqual("/bin/sh", prefs.entrypoint)

        tool_cfg: dict[str, object] = {}
        _store_extra_mount_preferences(tool_cfg, prefs)
        self.assertEqual({"docker": True}, tool_cfg["mounts"])
        self.assertEqual("/bin/sh", tool_cfg["entrypoint"])

    def test_resolve_entrypoint_path(self) -> None:
        resolved = _resolve_entrypoint_path("./entrypoint.sh")
        self.assertTrue(resolved.is_absolute())

    def test_validate_entrypoint_path_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing = Path(tmp_dir) / "missing.sh"
            with self.assertRaises(CliError):
                _validate_entrypoint_path(missing)

            entrypoint = Path(tmp_dir) / "entrypoint.sh"
            entrypoint.write_text("#!/bin/sh\necho ok\n", encoding="utf-8")
            with mock.patch("os.access", return_value=False):
                with self.assertRaises(CliError):
                    _validate_entrypoint_path(entrypoint)

    def test_build_extra_mounts_persists_entrypoint(self) -> None:
        prefs = _ExtraMountPreferences()
        with (
            mock.patch("aicage.runtime.extra_mounts._validate_entrypoint_path"),
            mock.patch("aicage.runtime.extra_mounts.prompt_yes_no", return_value=True),
        ):
            mounts, updated = _build_extra_mounts("./entrypoint.sh", False, prefs)

        self.assertTrue(updated)
        self.assertEqual(str(Path("./entrypoint.sh").expanduser().resolve()), prefs.entrypoint)
        self.assertEqual(1, len(mounts))
        self.assertTrue(mounts[0].read_only)

    def test_build_extra_mounts_persists_docker_socket(self) -> None:
        prefs = _ExtraMountPreferences()
        with mock.patch("aicage.runtime.extra_mounts.prompt_yes_no", return_value=True):
            mounts, updated = _build_extra_mounts(None, True, prefs)

        self.assertTrue(updated)
        self.assertTrue(prefs.docker_socket)
        self.assertEqual(1, len(mounts))
        self.assertEqual(Path("/run/docker.sock"), mounts[0].container_path)

    def test_build_extra_mounts_uses_persisted_docker_socket(self) -> None:
        prefs = _ExtraMountPreferences(docker_socket=True)
        with mock.patch("aicage.runtime.extra_mounts.prompt_yes_no") as prompt_mock:
            mounts, updated = _build_extra_mounts(None, False, prefs)

        self.assertFalse(updated)
        self.assertEqual(1, len(mounts))
        prompt_mock.assert_not_called()
