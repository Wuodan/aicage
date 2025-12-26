import tempfile
from pathlib import Path
from unittest import TestCase

from aicage.errors import CliError
from aicage.registry.images_metadata.models import ImagesMetadata
from aicage.runtime.tool_config import resolve_tool_config


class ToolConfigTests(TestCase):
    def test_resolve_tool_config_reads_metadata_and_creates_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tool_dir = Path(tmp_dir) / ".codex"
            metadata = ImagesMetadata.from_mapping(
                {
                    "aicage-image": {"version": "0.3.3"},
                    "aicage-image-base": {"version": "0.3.3"},
                    "bases": {
                        "ubuntu": {
                            "root_image": "ubuntu:latest",
                            "base_image_distro": "Ubuntu",
                            "base_image_description": "Default",
                            "os_installer": "distro/debian/install.sh",
                            "test_suite": "default",
                        }
                    },
                    "tool": {
                        "codex": {
                            "tool_path": str(tool_dir),
                            "tool_full_name": "Codex CLI",
                            "tool_homepage": "https://example.com",
                            "valid_bases": ["ubuntu"],
                        }
                    },
                }
            )
            config = resolve_tool_config("codex", metadata)
            self.assertEqual(str(tool_dir), config.tool_path)
            self.assertTrue(config.tool_config_host.exists())

    def test_resolve_tool_config_missing_tool_raises(self) -> None:
        metadata = ImagesMetadata.from_mapping(
            {
                "aicage-image": {"version": "0.3.3"},
                "aicage-image-base": {"version": "0.3.3"},
                "bases": {},
                "tool": {},
            }
        )
        with self.assertRaises(CliError):
            resolve_tool_config("codex", metadata)
