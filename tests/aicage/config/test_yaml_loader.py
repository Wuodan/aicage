import tempfile
from pathlib import Path
from unittest import TestCase

from aicage.config.errors import ConfigError
from aicage.config.yaml_loader import load_yaml


class YamlLoaderTests(TestCase):
    def test_load_yaml_reads_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "config.yaml"
            path.write_text("name: value\n", encoding="utf-8")

            payload = load_yaml(path)

        self.assertEqual({"name": "value"}, payload)

    def test_load_yaml_rejects_non_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "config.yaml"
            path.write_text("- value\n", encoding="utf-8")

            with self.assertRaises(ConfigError):
                load_yaml(path)

    def test_load_yaml_reports_parse_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            bad_file = Path(tmp_dir) / "bad.yaml"
            bad_file.write_text("key: [unterminated", encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_yaml(bad_file)
