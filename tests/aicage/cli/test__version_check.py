import io
from unittest import TestCase, mock

from aicage.cli import _version_check as version_check


class VersionCheckTests(TestCase):
    def test_maybe_prompt_update_skips_unknown_version(self) -> None:
        with (
            mock.patch("aicage.cli._version_check._check_for_update") as check_mock,
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            version_check.maybe_prompt_update(version_check._UNKNOWN_VERSION)

        check_mock.assert_not_called()
        self.assertEqual("", stdout.getvalue())

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
            mock.patch("aicage.cli._version_check.prompt_update_aicage", return_value=False),
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            version_check.maybe_prompt_update("1.0.0")

        output = stdout.getvalue()
        self.assertIn("Update with: pipx upgrade aicage", output)

    def test_maybe_prompt_update_yes_runs_upgrade(self) -> None:
        with (
            mock.patch("aicage.cli._version_check._check_for_update", return_value="1.2.3"),
            mock.patch("aicage.cli._version_check.prompt_update_aicage", return_value=True),
            mock.patch("aicage.cli._version_check._run_upgrade") as upgrade_mock,
        ):
            version_check.maybe_prompt_update("1.0.0")

        upgrade_mock.assert_called_once()
