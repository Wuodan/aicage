from unittest import TestCase

from aicage import config


class ConfigInitTests(TestCase):
    def test_exports(self) -> None:
        self.assertIn("SettingsStore", config.__all__)
        self.assertIn("RunConfig", config.__all__)
