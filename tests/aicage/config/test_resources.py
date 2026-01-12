from unittest import TestCase

from aicage.config.resources import find_packaged_path


class ResourcesTests(TestCase):
    def test_find_packaged_path_finds_repo_config(self) -> None:
        path = find_packaged_path("config.yaml")

        self.assertTrue(path.is_file())
        self.assertEqual("config.yaml", path.name)
