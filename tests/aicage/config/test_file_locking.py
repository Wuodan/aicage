from contextlib import contextmanager
from pathlib import Path
from unittest import TestCase, mock

from aicage.config import _file_locking as file_locking


class FileLockingTests(TestCase):
    def test_lock_project_config_creates_paths_and_uses_portalocker(self) -> None:
        class FakeLock:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        with mock.patch("aicage.config._file_locking.portalocker.Lock", return_value=FakeLock()) as lock_mock:
            project_path = Path("/tmp/aicage/test/project/lockfile")
            with file_locking.lock_project_config(project_path):
                pass

        self.assertTrue(project_path.parent.exists())
        lock_mock.assert_any_call(str(project_path), timeout=30, mode="a+")
        self.assertEqual(1, lock_mock.call_count)

    def test_lock_project_config_uses_one_lock(self) -> None:
        @contextmanager
        def fake_lock(path: Path):
            yield

        with mock.patch(
            "aicage.config._file_locking._lock_file",
            side_effect=[fake_lock(Path("/tmp/project"))],
        ) as lock_mock:
            with file_locking.lock_project_config(Path("/tmp/project")):
                pass
        self.assertEqual(1, lock_mock.call_count)
