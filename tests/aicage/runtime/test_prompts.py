from unittest import TestCase, mock

from aicage.errors import CliError
from aicage.runtime.prompts import BaseSelectionRequest, prompt_for_base


class PromptTests(TestCase):
    def test_prompt_requires_tty(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=False):
            with self.assertRaises(CliError):
                prompt_for_base(BaseSelectionRequest(tool="codex", default_base="ubuntu", available=["ubuntu"]))

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
