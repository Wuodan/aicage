from unittest import TestCase, mock

from aicage.errors import CliError
from aicage.runtime.prompts import (
    BaseSelectionRequest,
    ensure_tty_for_prompt,
    prompt_for_base,
    prompt_yes_no,
)


class PromptTests(TestCase):
    def test_prompt_requires_tty(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=False):
            with self.assertRaises(CliError):
                ensure_tty_for_prompt()

    def test_prompt_validates_choice(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch(
            "builtins.input", return_value="fedora"
        ):
            with self.assertRaises(CliError):
                prompt_for_base(BaseSelectionRequest(tool="codex", default_base="ubuntu", available=["ubuntu"]))

    def test_prompt_accepts_number_and_default(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", side_effect=["2", ""]):
            choice = prompt_for_base(
                BaseSelectionRequest(tool="codex", default_base="ubuntu", available=["alpine", "ubuntu"])
            )
            self.assertEqual("ubuntu", choice)
            default_choice = prompt_for_base(
                BaseSelectionRequest(tool="codex", default_base="ubuntu", available=["ubuntu"])
            )
            self.assertEqual("ubuntu", default_choice)
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", return_value="3"):
            with self.assertRaises(CliError):
                prompt_for_base(
                    BaseSelectionRequest(tool="codex", default_base="ubuntu", available=["alpine", "ubuntu"])
                )

    def test_prompt_accepts_default_without_list(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", return_value=""):
            choice = prompt_for_base(BaseSelectionRequest(tool="codex", default_base="ubuntu", available=[]))
        self.assertEqual("ubuntu", choice)

    def test_prompt_yes_no_defaults(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", return_value=""):
            self.assertTrue(prompt_yes_no("Continue?", default=True))
            self.assertFalse(prompt_yes_no("Continue?", default=False))

    def test_prompt_yes_no_parses_input(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", return_value="y"):
            self.assertTrue(prompt_yes_no("Continue?", default=False))
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", return_value="no"):
            self.assertFalse(prompt_yes_no("Continue?", default=True))
