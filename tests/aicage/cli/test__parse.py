import io
from unittest import TestCase, mock

from aicage import __version__
from aicage.cli._errors import CliError
from aicage.cli._parse import parse_cli


class ParseCliTests(TestCase):
    def test_parse_cli_with_docker_args(self) -> None:
        with self.assertRaises(CliError) as ctx:
            parse_cli(["--dry-run", "--network=host", "codex", "--foo"])
        self.assertEqual("Docker args require '--' before the agent.", str(ctx.exception))

    def test_parse_cli_with_separator(self) -> None:
        parsed = parse_cli(["--dry-run", "--", "codex", "--bar"])
        self.assertTrue(parsed.dry_run)
        self.assertEqual("", parsed.docker_args)
        self.assertEqual("codex", parsed.agent)
        self.assertEqual(["--bar"], parsed.agent_args)

    def test_parse_cli_with_separator_and_docker_args(self) -> None:
        parsed = parse_cli(["--dry-run", "-v", "/run/docker.sock:/run/docker.sock", "--", "codex", "--bar"])
        self.assertTrue(parsed.dry_run)
        self.assertEqual("-v /run/docker.sock:/run/docker.sock", parsed.docker_args)
        self.assertEqual("codex", parsed.agent)
        self.assertEqual(["--bar"], parsed.agent_args)
        self.assertIsNone(parsed.entrypoint)
        self.assertFalse(parsed.docker_socket)
        self.assertIsNone(parsed.config_action)

    def test_parse_cli_without_docker_args(self) -> None:
        parsed = parse_cli(["codex", "--flag"])
        self.assertFalse(parsed.dry_run)
        self.assertEqual("", parsed.docker_args)
        self.assertEqual("codex", parsed.agent)
        self.assertEqual(["--flag"], parsed.agent_args)
        self.assertIsNone(parsed.entrypoint)
        self.assertFalse(parsed.docker_socket)
        self.assertIsNone(parsed.config_action)

    def test_parse_cli_help_exits(self) -> None:
        with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            with self.assertRaises(SystemExit) as ctx:
                parse_cli(["--help"])
        self.assertEqual(0, ctx.exception.code)
        self.assertIn("Usage:", stdout.getvalue())

    def test_parse_cli_version_exits(self) -> None:
        with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            with self.assertRaises(SystemExit) as ctx:
                parse_cli(["--version"])
        self.assertEqual(0, ctx.exception.code)
        self.assertEqual(f"{__version__}\n", stdout.getvalue())

    def test_parse_cli_short_version_exits(self) -> None:
        with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            with self.assertRaises(SystemExit) as ctx:
                parse_cli(["-v"])
        self.assertEqual(0, ctx.exception.code)
        self.assertEqual(f"{__version__}\n", stdout.getvalue())

    def test_parse_cli_requires_arguments(self) -> None:
        with self.assertRaises(CliError):
            parse_cli([])

    def test_parse_cli_requires_agent_after_separator(self) -> None:
        with self.assertRaises(CliError):
            parse_cli(["--"])

    def test_parse_cli_requires_agent_name(self) -> None:
        with self.assertRaises(CliError):
            parse_cli([""])

    def test_parse_cli_requires_separator_for_docker_args(self) -> None:
        with self.assertRaises(CliError) as ctx:
            parse_cli(["-v", "/tmp/folder:/tmp/folder", "codex"])
        self.assertEqual("Docker args require '--' before the agent.", str(ctx.exception))

    def test_parse_cli_config_print(self) -> None:
        parsed = parse_cli(["--config", "print"])
        self.assertEqual("print", parsed.config_action)
        self.assertEqual("", parsed.docker_args)
        self.assertEqual("", parsed.agent)
        self.assertEqual([], parsed.agent_args)

    def test_parse_cli_config_print_rejects_args(self) -> None:
        with self.assertRaises(CliError):
            parse_cli(["--config", "print", "codex"])

    def test_parse_cli_flags_before_separator(self) -> None:
        parsed = parse_cli(
            [
                "--docker",
                "--aicage-entrypoint",
                "/tmp/entrypoint.sh",
                "--dry-run",
                "--",
                "codex",
            ]
        )
        self.assertTrue(parsed.dry_run)
        self.assertTrue(parsed.docker_socket)
        self.assertEqual("/tmp/entrypoint.sh", parsed.entrypoint)
        self.assertEqual("", parsed.docker_args)
        self.assertEqual("codex", parsed.agent)
