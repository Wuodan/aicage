from unittest import TestCase

from aicage.runtime import auth


class AuthInitTests(TestCase):
    def test_exports(self) -> None:
        self.assertEqual([], auth.__all__)
