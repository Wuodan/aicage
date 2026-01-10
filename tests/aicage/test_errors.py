from unittest import TestCase

from aicage.errors import AicageError


class AicageErrorTests(TestCase):
    def test_error_message(self) -> None:
        err = AicageError("boom")
        self.assertEqual("boom", str(err))
