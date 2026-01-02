from unittest import TestCase

from aicage.runtime import mounts


class MountsInitTests(TestCase):
    def test_exports(self) -> None:
        self.assertFalse(hasattr(mounts, "__all__"))
        self.assertTrue(callable(mounts.resolve_mounts))
