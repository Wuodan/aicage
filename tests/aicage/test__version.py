from unittest import TestCase

from aicage import _version


class VersionModuleTests(TestCase):
    def test_version_exports(self) -> None:
        self.assertIn("__version__", _version.__all__)
        self.assertIsInstance(_version.__version__, str)
