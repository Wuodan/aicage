from unittest import TestCase

from aicage import _lists


class ListsTests(TestCase):
    def test_read_str_list_or_empty_returns_empty_for_non_list(self) -> None:
        self.assertEqual([], _lists.read_str_list_or_empty(None))
        self.assertEqual([], _lists.read_str_list_or_empty("value"))

    def test_read_str_list_or_empty_filters_invalid_items(self) -> None:
        value = ["one", "", "two", 3, None, "three"]
        self.assertEqual(["one", "two", "three"], _lists.read_str_list_or_empty(value))
