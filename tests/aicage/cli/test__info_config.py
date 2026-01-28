import io
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.cli import _info_config as info_config
from aicage.config.project_config import _PROJECT_AGENTS_KEY


class InfoConfigTests(TestCase):
    def test_info_project_config_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "project.yml"
            store = mock.Mock()
            store.project_config_path.return_value = config_path
            with (
                mock.patch("aicage.cli._info_config.SettingsStore", return_value=store),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                info_config.info_project_config()

        output = stdout.getvalue()
        self.assertIn("Project config path:", output)
        self.assertIn(str(config_path), output)
        self.assertIn("(missing)", output)

    def test_info_project_config_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "project.yml"
            config_path.write_text("", encoding="utf-8")
            store = mock.Mock()
            store.project_config_path.return_value = config_path
            with (
                mock.patch("aicage.cli._info_config.SettingsStore", return_value=store),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                info_config.info_project_config()

        self.assertIn("(empty)", stdout.getvalue())

    def test_info_project_config_contents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "project.yml"
            config_path.write_text(f"{_PROJECT_AGENTS_KEY}: {{}}", encoding="utf-8")
            store = mock.Mock()
            store.project_config_path.return_value = config_path
            with (
                mock.patch("aicage.cli._info_config.SettingsStore", return_value=store),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                info_config.info_project_config()

        self.assertIn(f"{_PROJECT_AGENTS_KEY}: {{}}", stdout.getvalue())
