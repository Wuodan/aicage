from unittest import TestCase

from aicage.runtime import mounts


class MountsInitTests(TestCase):
    def test_exports(self) -> None:
        self.assertEqual(["resolve_mounts"], mounts.__all__)
