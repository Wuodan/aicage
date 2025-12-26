import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.config_store import SettingsStore
from aicage.config.global_config import GlobalConfig
from aicage.errors import CliError
from aicage.registry.images_metadata import loader
from aicage.registry.images_metadata.loader import load_images_metadata


class ImagesMetadataLoaderTests(TestCase):
    def test_load_images_metadata_downloads_and_caches(self) -> None:
        payload = _valid_payload()
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = SettingsStore(base_dir=Path(tmp_dir), ensure_global_config=False)
            global_cfg = _build_global_config()
            with mock.patch(
                "aicage.registry.images_metadata.loader.download_images_metadata",
                return_value=payload,
            ):
                metadata = load_images_metadata(global_cfg, store)

            cached = (Path(tmp_dir) / "images-metadata.yaml").read_text(encoding="utf-8")
            self.assertEqual(payload, cached)
            self.assertEqual("0.3.3", metadata.aicage_image.version)

    def test_load_images_metadata_uses_cache_on_download_failure(self) -> None:
        payload = _valid_payload()
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = SettingsStore(base_dir=Path(tmp_dir), ensure_global_config=False)
            (Path(tmp_dir) / "images-metadata.yaml").write_text(payload, encoding="utf-8")
            global_cfg = _build_global_config()
            with mock.patch(
                "aicage.registry.images_metadata.loader.download_images_metadata",
                side_effect=CliError("boom"),
            ):
                metadata = load_images_metadata(global_cfg, store)
            self.assertEqual("0.3.3", metadata.aicage_image.version)

    def test_load_images_metadata_raises_without_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = SettingsStore(base_dir=Path(tmp_dir), ensure_global_config=False)
            global_cfg = _build_global_config()
            with mock.patch(
                "aicage.registry.images_metadata.loader.download_images_metadata",
                side_effect=CliError("boom"),
            ):
                with self.assertRaises(CliError):
                    load_images_metadata(global_cfg, store)

    def test_download_with_retries_respects_attempts(self) -> None:
        global_cfg = _build_global_config(retries=2, backoff=0.0)
        with (
            mock.patch(
                "aicage.registry.images_metadata.loader.download_images_metadata",
                side_effect=[CliError("nope"), "payload"],
            ) as download_mock,
            mock.patch("aicage.registry.images_metadata.loader.time.sleep") as sleep_mock,
        ):
            payload, error = loader._download_with_retries(global_cfg)

        self.assertEqual("payload", payload)
        self.assertIsNone(error)
        self.assertEqual(2, download_mock.call_count)
        sleep_mock.assert_called_once_with(0.0)


def _valid_payload() -> str:
    return """
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


def _build_global_config(retries: int = 3, backoff: float = 1.5) -> GlobalConfig:
    return GlobalConfig(
        image_registry="ghcr.io",
        image_registry_api_url="https://ghcr.io/v2",
        image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
        image_repository="aicage/aicage",
        default_image_base="ubuntu",
        images_metadata_release_api_url="https://api.github.com/repos/aicage/aicage-image/releases/latest",
        images_metadata_asset_name="images-metadata.yaml",
        images_metadata_download_retries=retries,
        images_metadata_retry_backoff_seconds=backoff,
    )
