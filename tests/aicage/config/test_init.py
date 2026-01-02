from unittest import TestCase

from aicage import config


class ConfigInitTests(TestCase):
    def test_exports(self) -> None:
        self.assertFalse(hasattr(config, "__all__"))
        self.assertTrue(hasattr(config, "SettingsStore"))
        self.assertTrue(hasattr(config, "RunConfig"))
