from unittest import TestCase

from aicage.runtime import mounts
from aicage.runtime.mounts.resolver import resolve_mounts


class MountsInitTests(TestCase):
    def test_exports(self) -> None:
        self.assertFalse(hasattr(mounts, "__all__"))
        self.assertTrue(callable(resolve_mounts))
