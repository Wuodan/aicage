from pathlib import Path
from unittest import TestCase, mock

from aicage.registry.local_build import _logs


class LocalBuildLogsTests(TestCase):
    def test_log_paths_use_timestamp(self) -> None:
        with mock.patch("aicage.registry.local_build._logs._timestamp", return_value="stamp"):
            build_log = _logs.build_log_path("claude", "ubuntu")

        self.assertTrue(str(build_log).endswith("claude-ubuntu-stamp.log"))

    def test_log_paths_use_base_dir(self) -> None:
        with (
            mock.patch("aicage.registry.local_build._logs._DEFAULT_LOG_DIR", "/tmp/logs"),
            mock.patch("aicage.registry.local_build._logs._timestamp", return_value="stamp"),
        ):
            build_log = _logs.build_log_path("claude", "ubuntu")
        self.assertEqual(Path("/tmp/logs") / "claude-ubuntu-stamp.log", build_log)
