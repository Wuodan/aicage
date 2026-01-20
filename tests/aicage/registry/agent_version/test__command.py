import io
import tempfile
from pathlib import Path
from subprocess import CompletedProcess
from unittest import TestCase, mock

from aicage.registry.agent_version import _command


class AgentVersionCommandTests(TestCase):
    def test_run_host_uses_bash_for_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            script_path = Path(tmp_dir) / "version.sh"
            script_path.write_text("echo 1.2.3\n", encoding="utf-8")
            with (
                mock.patch("aicage.registry.agent_version._command.os.access", return_value=False),
                mock.patch(
                    "aicage.registry.agent_version._command.subprocess.run",
                    return_value=CompletedProcess([], 0, stdout="1.2.3\n", stderr=""),
                ) as run_mock,
                mock.patch("sys.stderr", new_callable=io.StringIO),
            ):
                result = _command.run_host(script_path)
            run_mock.assert_called_once_with(
                ["bash", str(script_path)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertTrue(result.success)
            self.assertEqual("1.2.3", result.output)

    def test_run_host_returns_error_on_exception(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            script_path = Path(tmp_dir) / "version.sh"
            script_path.write_text("echo 1.2.3\n", encoding="utf-8")
            with (
                mock.patch(
                    "aicage.registry.agent_version._command.subprocess.run",
                    side_effect=FileNotFoundError("missing"),
                ),
            ):
                result = _command.run_host(script_path)
            self.assertFalse(result.success)
            self.assertEqual("missing", result.error)

    def test_run_version_check_image_returns_error_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            definition_dir = Path(tmp_dir)
            with mock.patch(
                "aicage.registry.agent_version._command.run_builder_version_check",
                return_value=CompletedProcess([], 1, stdout="", stderr="failed"),
            ):
                result = _command.run_version_check_image(
                    "ghcr.io/aicage/aicage-image-util:agent-version",
                    definition_dir,
                )
            self.assertFalse(result.success)
            self.assertEqual("failed", result.error)
