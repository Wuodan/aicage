from unittest import TestCase

from aicage.errors import CliError
from aicage.registry.custom_agent import _validation


class CustomAgentValidationTests(TestCase):
    def test_expect_string_rejects_empty(self) -> None:
        with self.assertRaises(CliError):
            _validation.expect_string(" ", "agent_path")

    def test_expect_bool_rejects_non_bool(self) -> None:
        with self.assertRaises(CliError):
            _validation.expect_bool("true", "redistributable")

    def test_maybe_str_list_rejects_non_string_items(self) -> None:
        with self.assertRaises(CliError):
            _validation.maybe_str_list(["ok", ""], "base_exclude")

    def test_expect_keys_rejects_missing_required(self) -> None:
        with self.assertRaises(CliError):
            _validation.expect_keys(
                {"agent_path": "~/.custom"},
                required={"agent_path", "agent_full_name"},
                optional=set(),
                context="custom agent",
            )
