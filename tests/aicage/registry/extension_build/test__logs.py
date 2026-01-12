from pathlib import Path
from unittest import TestCase, mock

from aicage.registry.extension_build import _logs


class ExtensionBuildLogsTests(TestCase):
    def test_build_log_path_for_image(self) -> None:
        with (
            mock.patch("aicage.registry.extension_build._logs._DEFAULT_LOG_DIR", "/tmp/logs"),
            mock.patch("aicage.registry.extension_build._logs.timestamp", return_value="stamp"),
        ):
            log_path = _logs.build_log_path_for_image("aicage:codex-ubuntu")

        self.assertEqual(Path("/tmp/logs") / "aicage_codex-ubuntu-stamp.log", log_path)
