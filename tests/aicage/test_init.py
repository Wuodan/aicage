from unittest import TestCase

import aicage


class PackageInitTests(TestCase):
    def test_version_export(self) -> None:
        self.assertFalse(hasattr(aicage, "__all__"))
        self.assertIsInstance(aicage.__version__, str)
