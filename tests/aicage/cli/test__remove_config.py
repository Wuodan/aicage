import io
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.cli import _remove_config as remove_config


class RemoveConfigTests(TestCase):
    def test_remove_project_config_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "project.yml"
            store = mock.Mock()
            store.project_config_path.return_value = config_path
            with (
                mock.patch("aicage.cli._remove_config.SettingsStore", return_value=store),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                remove_config.remove_project_config()

        output = stdout.getvalue()
        self.assertIn("Project config not found:", output)
        self.assertIn(str(config_path), output)

    def test_remove_project_config_existing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "project.yml"
            config_path.write_text("agents: {}", encoding="utf-8")
            store = mock.Mock()
            store.project_config_path.return_value = config_path
            with (
                mock.patch("aicage.cli._remove_config.SettingsStore", return_value=store),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                remove_config.remove_project_config()

        output = stdout.getvalue()
        self.assertIn("Project config removed:", output)
        self.assertIn(str(config_path), output)
        self.assertFalse(config_path.exists())
