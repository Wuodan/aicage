from unittest import TestCase, mock

from aicage.runtime.errors import RuntimeExecutionError
from aicage.runtime.prompts.extensions import ExtensionOption, prompt_for_extensions


class PromptExtensionsTests(TestCase):
    def test_prompt_for_extensions_returns_empty_for_no_options(self) -> None:
        self.assertEqual([], prompt_for_extensions([]))

    def test_prompt_for_extensions_accepts_numbers_and_names(self) -> None:
        options = [
            ExtensionOption(name="one", description="First"),
            ExtensionOption(name="two", description="Second"),
        ]
        with (
            mock.patch("aicage.runtime.prompts.extensions.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value="2,one"),
        ):
            selection = prompt_for_extensions(options)
        self.assertEqual(["two", "one"], selection)

    def test_prompt_for_extensions_returns_empty_on_blank_input(self) -> None:
        options = [
            ExtensionOption(name="one", description="First"),
            ExtensionOption(name="two", description="Second"),
        ]
        with (
            mock.patch("aicage.runtime.prompts.extensions.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value=""),
        ):
            selection = prompt_for_extensions(options)
        self.assertEqual([], selection)

    def test_prompt_for_extensions_rejects_duplicates(self) -> None:
        options = [
            ExtensionOption(name="one", description="First"),
            ExtensionOption(name="two", description="Second"),
        ]
        with (
            mock.patch("aicage.runtime.prompts.extensions.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value="1,one"),
        ):
            with self.assertRaises(RuntimeExecutionError):
                prompt_for_extensions(options)

    def test_prompt_for_extensions_rejects_invalid_choice(self) -> None:
        options = [
            ExtensionOption(name="one", description="First"),
            ExtensionOption(name="two", description="Second"),
        ]
        with (
            mock.patch("aicage.runtime.prompts.extensions.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value="3"),
        ):
            with self.assertRaises(RuntimeExecutionError):
                prompt_for_extensions(options)

    def test_prompt_for_extensions_rejects_invalid_name(self) -> None:
        options = [
            ExtensionOption(name="one", description="First"),
            ExtensionOption(name="two", description="Second"),
        ]
        with (
            mock.patch("aicage.runtime.prompts.extensions.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value="unknown"),
        ):
            with self.assertRaises(RuntimeExecutionError):
                prompt_for_extensions(options)
