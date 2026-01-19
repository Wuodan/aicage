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

    def test_prompt_persist_entrypoint_delegates(self) -> None:
        with mock.patch("aicage.runtime.prompts.confirm._prompt_yes_no", return_value=True) as prompt_mock:
            self.assertTrue(confirm.prompt_persist_entrypoint(Path("/tmp/entrypoint")))
        prompt_mock.assert_called_once_with(
            f"Persist entrypoint '{Path('/tmp/entrypoint')}' for this project?",
            default=True,
        )

    def test_prompt_persist_docker_socket_delegates(self) -> None:
        with mock.patch("aicage.runtime.prompts.confirm._prompt_yes_no", return_value=True) as prompt_mock:
            self.assertTrue(confirm.prompt_persist_docker_socket())
        prompt_mock.assert_called_once_with(
            "Persist mounting the Docker socket for this project?",
            default=True,
        )

    def test_prompt_mount_git_config_delegates(self) -> None:
        with mock.patch("aicage.runtime.prompts.confirm._prompt_yes_no", return_value=True) as prompt_mock:
            self.assertTrue(confirm.prompt_mount_git_config(Path("/tmp/gitconfig")))
        prompt_mock.assert_called_once_with(
            f"Mount Git config from '{Path('/tmp/gitconfig')}' so Git uses your usual name/email?",
            default=True,
        )

    def test_prompt_mount_gpg_keys_delegates(self) -> None:
        with mock.patch("aicage.runtime.prompts.confirm._prompt_yes_no", return_value=True) as prompt_mock:
            self.assertTrue(confirm.prompt_mount_gpg_keys(Path("/tmp/gpg")))
        prompt_mock.assert_called_once_with(
            f"Mount GnuPG keys from '{Path('/tmp/gpg')}' so Git signing works like on your host?",
            default=True,
        )

    def test_prompt_mount_ssh_keys_delegates(self) -> None:
        with mock.patch("aicage.runtime.prompts.confirm._prompt_yes_no", return_value=True) as prompt_mock:
            self.assertTrue(confirm.prompt_mount_ssh_keys(Path("/tmp/ssh")))
        prompt_mock.assert_called_once_with(
            f"Mount SSH keys from '{Path('/tmp/ssh')}' so Git signing works like on your host?",
            default=True,
        )

    def test_prompt_persist_docker_args_replaces_existing(self) -> None:
        with mock.patch("aicage.runtime.prompts.confirm._prompt_yes_no", return_value=True) as prompt_mock:
            self.assertTrue(confirm.prompt_persist_docker_args("-it", "--rm"))
        prompt_mock.assert_called_once_with(
            "Persist docker run args '-it' for this project (replacing '--rm')?",
            default=True,
        )
