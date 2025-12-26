from unittest import TestCase

from aicage.errors import CliError
from aicage.registry.images_metadata.models import ImagesMetadata


class ImagesMetadataModelTests(TestCase):
    def test_from_yaml_parses_valid_payload(self) -> None:
        payload = """
aicage-image:
  version: 0.3.3
aicage-image-base:
  version: 0.3.3
bases:
  ubuntu:
    root_image: ubuntu:latest
    base_image_distro: Ubuntu
    base_image_description: Good default
    os_installer: distro/debian/install.sh
    test_suite: default
tool:
  codex:
    tool_path: ~/.codex
    tool_full_name: Codex CLI
    tool_homepage: https://example.com
    valid_bases:
      - ubuntu
"""
        metadata = ImagesMetadata.from_yaml(payload)
        self.assertEqual("0.3.3", metadata.aicage_image.version)
        self.assertEqual("0.3.3", metadata.aicage_image_base.version)
        self.assertIn("ubuntu", metadata.bases)
        self.assertIn("codex", metadata.tools)
        self.assertEqual(["ubuntu"], metadata.tools["codex"].valid_bases)

    def test_from_mapping_rejects_unknown_top_level_keys(self) -> None:
        data = {
            "aicage-image": {"version": "0.3.3"},
            "aicage-image-base": {"version": "0.3.3"},
            "bases": {},
            "tool": {},
            "extra": {},
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_unknown_tool_keys(self) -> None:
        data = {
            "aicage-image": {"version": "0.3.3"},
            "aicage-image-base": {"version": "0.3.3"},
            "bases": {},
            "tool": {
                "codex": {
                    "tool_path": "~/.codex",
                    "tool_full_name": "Codex CLI",
                    "tool_homepage": "https://example.com",
                    "valid_bases": ["ubuntu"],
                    "extra": "nope",
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_missing_required_keys(self) -> None:
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping({})
