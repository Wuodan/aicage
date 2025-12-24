from unittest import TestCase

import aicage


class PackageInitTests(TestCase):
    def test_version_export(self) -> None:
        self.assertIn("__version__", aicage.__all__)
        self.assertIsInstance(aicage.__version__, str)
