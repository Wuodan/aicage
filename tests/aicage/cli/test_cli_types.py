from unittest import TestCase

from aicage.cli_types import ParsedArgs


class ParsedArgsTests(TestCase):
    def test_parsed_args_fields(self) -> None:
        parsed = ParsedArgs(
            dry_run=True,
            docker_args="--net=host",
            tool="codex",
            tool_args=["--flag"],
            entrypoint="/bin/bash",
            docker_socket=False,
            config_action=None,
        )

        self.assertTrue(parsed.dry_run)
        self.assertEqual("--net=host", parsed.docker_args)
        self.assertEqual("codex", parsed.tool)
        self.assertEqual(["--flag"], parsed.tool_args)
        self.assertEqual("/bin/bash", parsed.entrypoint)
        self.assertFalse(parsed.docker_socket)
        self.assertIsNone(parsed.config_action)
