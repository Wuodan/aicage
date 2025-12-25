from pathlib import Path
from unittest import TestCase, mock

from aicage.runtime.mounts._gpg import _resolve_gpg_home


class GpgHomeTests(TestCase):
    def test_resolve_gpg_home_parses_output(self) -> None:
        with mock.patch("aicage.runtime.mounts._gpg.capture_stdout", return_value="/home/user/.gnupg\n"):
            path = _resolve_gpg_home()
        self.assertEqual(Path("/home/user/.gnupg"), path)

    def test_resolve_gpg_home_handles_empty(self) -> None:
        with mock.patch("aicage.runtime.mounts._gpg.capture_stdout", return_value=""):
            path = _resolve_gpg_home()
        self.assertIsNone(path)
