from unittest import TestCase

from aicage.errors import CliError


class CliErrorTests(TestCase):
    def test_cli_error_message(self) -> None:
        err = CliError("boom")
        self.assertEqual("boom", str(err))
