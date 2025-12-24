from unittest import TestCase

from aicage import registry


class RegistryInitTests(TestCase):
    def test_exports(self) -> None:
        self.assertEqual({"pull_image", "select_tool_image"}, set(registry.__all__))
