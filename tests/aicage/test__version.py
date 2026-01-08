import importlib
from unittest import TestCase

from aicage import __version__


class VersionModuleTests(TestCase):
    def test_version_exports(self) -> None:
        self.assertIsInstance(__version__, str)
        try:
            module = importlib.import_module("aicage._version")
        except ImportError:
            return
        # Generated file from setuptools-scm; allow __all__ in version metadata.
        self.assertIsInstance(module.__version__, str)
