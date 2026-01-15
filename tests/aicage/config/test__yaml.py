from unittest import TestCase

from aicage.config import _yaml
from aicage.config.errors import ConfigError


class YamlHelpersTests(TestCase):
    def test_expect_string_rejects_blank(self) -> None:
        with self.assertRaises(ConfigError):
            _yaml.expect_string(" ", "value")

    def test_expect_string_returns_value(self) -> None:
        self.assertEqual("name", _yaml.expect_string("name", "value"))

    def test_expect_bool_rejects_non_bool(self) -> None:
        with self.assertRaises(ConfigError):
            _yaml.expect_bool("true", "flag")

    def test_expect_bool_returns_value(self) -> None:
        self.assertTrue(_yaml.expect_bool(True, "flag"))

    def test_read_str_list_rejects_non_list(self) -> None:
        with self.assertRaises(ConfigError):
            _yaml.read_str_list("value", "items")

    def test_read_str_list_rejects_blank_items(self) -> None:
        with self.assertRaises(ConfigError):
            _yaml.read_str_list(["ok", ""], "items")

    def test_read_str_list_returns_list(self) -> None:
        self.assertEqual(["one", "two"], _yaml.read_str_list(["one", "two"], "items"))

    def test_maybe_str_list_returns_none(self) -> None:
        self.assertIsNone(_yaml.maybe_str_list(None, "items"))

    def test_maybe_str_list_returns_list(self) -> None:
        self.assertEqual(["one"], _yaml.maybe_str_list(["one"], "items"))

    def test_expect_keys_rejects_missing(self) -> None:
        with self.assertRaises(ConfigError):
            _yaml.expect_keys({}, required={"name"}, optional=set(), context="payload")

    def test_expect_keys_rejects_unknown(self) -> None:
        with self.assertRaises(ConfigError):
            _yaml.expect_keys({"name": "x", "extra": True}, required={"name"}, optional=set(), context="payload")

    @staticmethod
    def test_expect_keys_accepts_valid() -> None:
        _yaml.expect_keys({"name": "x"}, required={"name"}, optional={"extra"}, context="payload")
