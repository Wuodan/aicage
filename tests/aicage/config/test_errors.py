from unittest import TestCase

from aicage.config.errors import ConfigError


class ConfigErrorTests(TestCase):
    def test_config_error_message(self) -> None:
        err = ConfigError("bad config")
        self.assertEqual("bad config", str(err))
