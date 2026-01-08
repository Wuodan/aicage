from pathlib import Path
from unittest import TestCase, mock

from aicage.runtime.prompts.missing_extensions import prompt_for_missing_extensions


class PromptMissingExtensionsTests(TestCase):
    def test_prompt_for_missing_extensions_lists_projects(self) -> None:
        other_projects = [("/tmp/one", Path("/tmp/one.yaml"))]
        with (
            mock.patch("aicage.runtime.prompts.missing_extensions.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value="fresh"),
            mock.patch("builtins.print") as print_mock,
        ):
            result = prompt_for_missing_extensions(
                agent="codex",
                missing=["ext"],
                stored_image_ref="aicage:codex-ubuntu",
                project_config_path=Path("/tmp/project.yaml"),
                other_projects=other_projects,
            )
        self.assertEqual("fresh", result)
        self.assertTrue(print_mock.called)

    def test_prompt_for_missing_extensions_no_projects(self) -> None:
        with (
            mock.patch("aicage.runtime.prompts.missing_extensions.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value="exit"),
            mock.patch("builtins.print") as print_mock,
        ):
            result = prompt_for_missing_extensions(
                agent="codex",
                missing=["ext"],
                stored_image_ref="",
                project_config_path=Path("/tmp/project.yaml"),
                other_projects=[],
            )
        self.assertEqual("exit", result)
        self.assertTrue(print_mock.called)
