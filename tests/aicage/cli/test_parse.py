import io
from unittest import TestCase, mock

from aicage import cli
from aicage.errors import CliError


class ParseCliTests(TestCase):
    def test_parse_with_docker_args(self) -> None:
        parsed = cli.parse_cli(["--dry-run", "--network=host", "codex", "--foo"])
        self.assertTrue(parsed.dry_run)
        self.assertEqual("--network=host", parsed.docker_args)
        self.assertEqual("codex", parsed.tool)
        self.assertEqual(["--foo"], parsed.tool_args)

    def test_parse_with_separator(self) -> None:
        parsed = cli.parse_cli(["--dry-run", "--", "codex", "--bar"])
        self.assertTrue(parsed.dry_run)
        self.assertEqual("", parsed.docker_args)
        self.assertEqual("codex", parsed.tool)
        self.assertEqual(["--bar"], parsed.tool_args)

    def test_parse_without_docker_args(self) -> None:
        parsed = cli.parse_cli(["codex", "--flag"])
        self.assertFalse(parsed.dry_run)
        self.assertEqual("", parsed.docker_args)
        self.assertEqual("codex", parsed.tool)
        self.assertEqual(["--flag"], parsed.tool_args)

    def test_parse_help_exits(self) -> None:
        with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            with self.assertRaises(SystemExit) as ctx:
                cli.parse_cli(["--help"])
        self.assertEqual(0, ctx.exception.code)
        self.assertIn("Usage:", stdout.getvalue())

    def test_parse_requires_arguments(self) -> None:
        with self.assertRaises(CliError):
            cli.parse_cli([])

    def test_parse_requires_tool_after_separator(self) -> None:
        with self.assertRaises(CliError):
            cli.parse_cli(["--"])

    def test_parse_requires_tool_name(self) -> None:
        with self.assertRaises(CliError):
            cli.parse_cli([""])
