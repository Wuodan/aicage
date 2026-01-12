from unittest import TestCase, mock

from aicage.runtime.errors import RuntimeExecutionError
from aicage.runtime.prompts._tty import ensure_tty_for_prompt


class PromptTtyTests(TestCase):
    def test_ensure_tty_for_prompt_raises_when_not_tty(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=False):
            with self.assertRaises(RuntimeExecutionError):
                ensure_tty_for_prompt()

    def test_ensure_tty_for_prompt_allows_tty(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=True):
            ensure_tty_for_prompt()
