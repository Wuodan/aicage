from pathlib import Path
from unittest import TestCase, mock

from aicage.registry import _logs


class RegistryLogsTests(TestCase):
    def test_pull_log_path_uses_timestamp(self) -> None:
        with mock.patch("aicage.registry._logs.timestamp", return_value="stamp"):
            log_path = _logs.pull_log_path("ghcr.io/aicage/aicage:codex-ubuntu")

        self.assertTrue(str(log_path).endswith("ghcr.io_aicage_aicage_codex-ubuntu-stamp.log"))

    def test_pull_log_path_uses_base_dir(self) -> None:
        with (
            mock.patch("aicage.registry._logs._DEFAULT_LOG_DIR", "/tmp/logs"),
            mock.patch("aicage.registry._logs.timestamp", return_value="stamp"),
        ):
            log_path = _logs.pull_log_path("ghcr.io/aicage/aicage:codex-ubuntu")
        self.assertEqual(Path("/tmp/logs") / "ghcr.io_aicage_aicage_codex-ubuntu-stamp.log", log_path)
