from unittest import TestCase

from aicage.config.errors import ConfigError
from aicage.config.global_config import GlobalConfig


class GlobalConfigTests(TestCase):
    def test_from_mapping_requires_fields(self) -> None:
        with self.assertRaises(ConfigError):
            GlobalConfig.from_mapping({"image_registry": "ghcr.io"})

    def test_round_trip_mapping(self) -> None:
        data = {
            "image_registry": "ghcr.io",
            "image_registry_api_url": "https://ghcr.io/v2",
            "image_registry_api_token_url": "https://ghcr.io/token",
            "image_repository": "aicage/aicage",
            "default_image_base": "ubuntu",
            "images_metadata_release_api_url": "https://api.github.com/repos/aicage/aicage-image/releases/latest",
            "images_metadata_asset_name": "images-metadata.yaml",
            "images_metadata_download_retries": 3,
            "images_metadata_retry_backoff_seconds": 1.5,
            "tools": {"codex": {"base": "ubuntu"}},
        }
        cfg = GlobalConfig.from_mapping(data)
        self.assertEqual(data, cfg.to_mapping())
