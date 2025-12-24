from unittest import TestCase

from aicage.registry import discovery


class DiscoveryInitTests(TestCase):
    def test_exports(self) -> None:
        self.assertEqual([], discovery.__all__)
