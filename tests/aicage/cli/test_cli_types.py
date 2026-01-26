from unittest import TestCase

from aicage.cli_types import ParsedArgs


class ParsedArgsTests(TestCase):
    def test_parsed_args_fields(self) -> None:
        parsed = ParsedArgs(
            dry_run=True,
            docker_args="--net=host",
            agent="codex",
            agent_args=["--flag"],
            docker_socket=False,
            config_action=None,
        )

        self.assertTrue(parsed.dry_run)
        self.assertEqual("--net=host", parsed.docker_args)
        self.assertEqual("codex", parsed.agent)
        self.assertEqual(["--flag"], parsed.agent_args)
        self.assertFalse(parsed.docker_socket)
        self.assertIsNone(parsed.config_action)
