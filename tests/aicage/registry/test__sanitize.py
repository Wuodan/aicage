from unittest import TestCase

from aicage.registry import _sanitize


class RegistrySanitizeTests(TestCase):
    def test_sanitize_replaces_reserved_characters(self) -> None:
        self.assertEqual("ghcr.io_aicage_image_tag", _sanitize.sanitize("ghcr.io/aicage:image:tag"))
