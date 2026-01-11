from datetime import datetime
from unittest import TestCase

from aicage.registry import _time


class RegistryTimeTests(TestCase):
    def test_now_iso_returns_iso_timestamp(self) -> None:
        value = _time.now_iso()
        parsed = datetime.fromisoformat(value)
        self.assertIsNotNone(parsed.tzinfo)

    def test_timestamp_returns_expected_format(self) -> None:
        value = _time.timestamp()
        parsed = datetime.strptime(value, "%Y%m%dT%H%M%SZ")
        self.assertIsNotNone(parsed)
