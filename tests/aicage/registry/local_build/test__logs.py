from pathlib import Path
from unittest import TestCase, mock

from aicage.registry.local_build import _logs


class LocalBuildLogsTests(TestCase):
    def test_build_log_path_uses_timestamp(self) -> None:
        with mock.patch("aicage.registry.local_build._logs.timestamp", return_value="stamp"):
            build_log = _logs.build_log_path("claude", "ubuntu")

        self.assertTrue(str(build_log).endswith("claude-ubuntu-stamp.log"))

    def test_build_log_path_uses_base_dir(self) -> None:
        with (
            mock.patch("aicage.registry.local_build._logs.IMAGE_BUILD_LOG_DIR", Path("/tmp/logs")),
            mock.patch("aicage.registry.local_build._logs.timestamp", return_value="stamp"),
        ):
            build_log = _logs.build_log_path("claude", "ubuntu")
        self.assertEqual(Path("/tmp/logs") / "claude-ubuntu-stamp.log", build_log)

    def test_custom_base_log_path_uses_base_dir(self) -> None:
        with (
            mock.patch("aicage.registry.local_build._logs.BASE_IMAGE_BUILD_LOG_DIR", Path("/tmp/logs")),
            mock.patch("aicage.registry.local_build._logs.timestamp", return_value="stamp"),
        ):
            build_log = _logs.custom_base_log_path("base")
        self.assertEqual(Path("/tmp/logs") / "base-stamp.log", build_log)
