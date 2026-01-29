import io
from unittest import TestCase, mock

from aicage.cli import _version_check as version_check


class VersionCheckTests(TestCase):
    def test_maybe_prompt_update_no_update(self) -> None:
        with (
            mock.patch("aicage.cli._version_check._check_for_update", return_value=None),
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            version_check.maybe_prompt_update("0.1.0")

        self.assertEqual("", stdout.getvalue())

    def test_maybe_prompt_update_non_tty(self) -> None:
        with (
            mock.patch("aicage.cli._version_check._check_for_update", return_value="1.2.3"),
            mock.patch("sys.stdin.isatty", return_value=False),
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            version_check.maybe_prompt_update("1.0.0")

        output = stdout.getvalue()
        self.assertIn("A newer version of aicage is available", output)
        self.assertIn("Update with: pipx upgrade aicage", output)
