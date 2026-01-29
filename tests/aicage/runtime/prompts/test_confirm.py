from pathlib import Path
from unittest import TestCase, mock

from aicage.runtime.prompts import confirm


class PromptConfirmTests(TestCase):
    def test__prompt_yes_no_accepts_default(self) -> None:
        with (
            mock.patch("aicage.runtime.prompts.confirm.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value=""),
        ):
            self.assertTrue(confirm._prompt_yes_no("Continue?", default=True))
            self.assertFalse(confirm._prompt_yes_no("Continue?", default=False))

    def test__prompt_yes_no_parses_response(self) -> None:
        with (
            mock.patch("aicage.runtime.prompts.confirm.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value="y"),
        ):
            self.assertTrue(confirm._prompt_yes_no("Continue?", default=False))

    def test_prompt_persist_docker_socket_delegates(self) -> None:
        with mock.patch("aicage.runtime.prompts.confirm._prompt_yes_no", return_value=True) as prompt_mock:
            self.assertTrue(confirm.prompt_persist_docker_socket())
        prompt_mock.assert_called_once_with(
            "Persist mounting the Docker socket for this project?",
            default=True,
        )

    def test_prompt_mount_git_support_delegates(self) -> None:
        items = [
            ("Git config (name/email)", Path("/tmp/gitconfig")),
            ("Git root (repository access)", Path("/tmp/root")),
        ]
        with mock.patch("aicage.runtime.prompts.confirm._prompt_yes_no", return_value=True) as prompt_mock:
            self.assertTrue(confirm.prompt_mount_git_support(items))
        prompt_mock.assert_called_once_with(
            "Enable Git support in the container by mounting:\n"
            f"  - Git config (name/email): {Path('/tmp/gitconfig')}\n"
            f"  - Git root (repository access): {Path('/tmp/root')}\n"
            "Proceed?",
            default=True,
        )

    def test_prompt_persist_docker_args_replaces_existing(self) -> None:
        with mock.patch("aicage.runtime.prompts.confirm._prompt_yes_no", return_value=True) as prompt_mock:
            self.assertTrue(confirm.prompt_persist_docker_args("-it", "--rm"))
        prompt_mock.assert_called_once_with(
            "Persist docker run args '-it' for this project (replacing '--rm')?",
            default=True,
        )

    def test_prompt_update_aicage_delegates(self) -> None:
        with mock.patch("aicage.runtime.prompts.confirm._prompt_yes_no", return_value=True) as prompt_mock:
            self.assertTrue(confirm.prompt_update_aicage("0.9.4", "0.9.5"))
        prompt_mock.assert_called_once_with(
            "A newer version of aicage is available (installed: 0.9.4, latest: 0.9.5). Update now?",
            default=True,
        )
