from pathlib import Path
from unittest import TestCase, mock

from aicage.runtime.prompts import confirm


class PromptConfirmTests(TestCase):
    def test_prompt_yes_no_accepts_default(self) -> None:
        with (
            mock.patch("aicage.runtime.prompts.confirm.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value=""),
        ):
            self.assertTrue(confirm.prompt_yes_no("Continue?", default=True))
            self.assertFalse(confirm.prompt_yes_no("Continue?", default=False))

    def test_prompt_yes_no_parses_response(self) -> None:
        with (
            mock.patch("aicage.runtime.prompts.confirm.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value="y"),
        ):
            self.assertTrue(confirm.prompt_yes_no("Continue?", default=False))

    def test_prompt_wrappers_delegate(self) -> None:
        with mock.patch("aicage.runtime.prompts.confirm.prompt_yes_no", return_value=True) as prompt_mock:
            self.assertTrue(confirm.prompt_persist_entrypoint(Path("/tmp/entrypoint")))
            self.assertTrue(confirm.prompt_persist_docker_socket())
            self.assertTrue(confirm.prompt_mount_git_config(Path("/tmp/gitconfig")))
            self.assertTrue(confirm.prompt_mount_gpg_keys(Path("/tmp/gpg")))
            self.assertTrue(confirm.prompt_mount_ssh_keys(Path("/tmp/ssh")))
            self.assertTrue(confirm.prompt_persist_docker_args("-it", None))
        self.assertEqual(6, prompt_mock.call_count)

    def test_prompt_persist_docker_args_replaces_existing(self) -> None:
        with mock.patch("aicage.runtime.prompts.confirm.prompt_yes_no", return_value=True) as prompt_mock:
            self.assertTrue(confirm.prompt_persist_docker_args("-it", "--rm"))
        prompt_mock.assert_called_once_with(
            "Persist docker run args '-it' for this project (replacing '--rm')?",
            default=True,
        )
