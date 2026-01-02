from unittest import TestCase

from aicage import runtime


class RuntimeInitTests(TestCase):
    def test_exports(self) -> None:
        self.assertFalse(hasattr(runtime, "__all__"))
