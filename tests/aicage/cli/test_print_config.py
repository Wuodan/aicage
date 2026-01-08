import io
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.cli import _print_config as print_config
from aicage.config.project_config import _PROJECT_AGENTS_KEY
from aicage.paths import PROJECT_CONFIG_FILENAME


class PrintConfigTests(TestCase):
    def test_print_project_config_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / PROJECT_CONFIG_FILENAME
            store = mock.Mock()
            store.project_config_path.return_value = config_path
            with (
                mock.patch("aicage.cli._print_config.SettingsStore", return_value=store),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                print_config.print_project_config()

        output = stdout.getvalue()
        self.assertIn("Project config path:", output)
        self.assertIn(str(config_path), output)
        self.assertIn("(missing)", output)

    def test_print_project_config_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / PROJECT_CONFIG_FILENAME
            config_path.write_text("", encoding="utf-8")
            store = mock.Mock()
            store.project_config_path.return_value = config_path
            with (
                mock.patch("aicage.cli._print_config.SettingsStore", return_value=store),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                print_config.print_project_config()

        self.assertIn("(empty)", stdout.getvalue())

    def test_print_project_config_contents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / PROJECT_CONFIG_FILENAME
            config_path.write_text(f"{_PROJECT_AGENTS_KEY}: {{}}", encoding="utf-8")
            store = mock.Mock()
            store.project_config_path.return_value = config_path
            with (
                mock.patch("aicage.cli._print_config.SettingsStore", return_value=store),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                print_config.print_project_config()

        self.assertIn(f"{_PROJECT_AGENTS_KEY}: {{}}", stdout.getvalue())
