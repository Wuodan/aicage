from pathlib import Path, PurePosixPath
from unittest import TestCase, mock

from aicage.paths import container_project_path


class PathsTests(TestCase):
    def test_container_project_path(self) -> None:
        path = Path(r"C:\development\github\aicage\aicage")
        expected = PurePosixPath("/mnt/c/development/github/aicage/aicage")

        with mock.patch("aicage.paths.os.name", "nt"):
            self.assertEqual(expected, container_project_path(path))

    def test_container_project_path_handles_extended_prefix(self) -> None:
        path = Path(r"\\?\C:\development\repo")
        expected = PurePosixPath("/mnt/c/development/repo")

        with mock.patch("aicage.paths.os.name", "nt"):
            self.assertEqual(expected, container_project_path(path))

    def test_container_project_path_posix(self) -> None:
        path = Path("/work/project")
        expected = PurePosixPath("/work/project")

        with mock.patch("aicage.paths.os.name", "posix"):
            self.assertEqual(expected, container_project_path(path))
