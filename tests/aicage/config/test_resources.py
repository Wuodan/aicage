from unittest import TestCase

from aicage.config.resources import find_packaged_path
from aicage.paths import IMAGES_METADATA_FILENAME


class ResourcesTests(TestCase):
    def test_find_packaged_path_finds_repo_config(self) -> None:
        path = find_packaged_path(IMAGES_METADATA_FILENAME)

        self.assertTrue(path.is_file())
        self.assertEqual(IMAGES_METADATA_FILENAME, path.name)
