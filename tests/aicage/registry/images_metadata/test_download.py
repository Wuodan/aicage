import json
from unittest import TestCase, mock

from aicage.config.global_config import GlobalConfig
from aicage.errors import CliError
from aicage.registry.images_metadata._download import download_images_metadata


class FakeResponse:
    def __init__(self, payload: str) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return self._payload.encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None


class ImagesMetadataDownloadTests(TestCase):
    def test_download_images_metadata_fetches_release_asset(self) -> None:
        release_payload = json.dumps(
            {
                "assets": [
                    {
                        "name": "images-metadata.yaml",
                        "browser_download_url": "https://example.com/images-metadata.yaml",
                    }
                ]
            }
        )
        yaml_payload = "aicage-image:\n  version: 0.3.3\n"
        responses = [FakeResponse(release_payload), FakeResponse(yaml_payload)]

        def fake_urlopen(request: object) -> FakeResponse:  # pylint: disable=unused-argument
            return responses.pop(0)

        global_cfg = _build_global_config()
        with mock.patch(
            "aicage.registry.images_metadata._download.urllib.request.urlopen",
            side_effect=fake_urlopen,
        ):
            payload = download_images_metadata(global_cfg)

        self.assertEqual(yaml_payload, payload)

    def test_download_images_metadata_raises_on_missing_asset(self) -> None:
        release_payload = json.dumps({"assets": []})
        global_cfg = _build_global_config()
        with mock.patch(
            "aicage.registry.images_metadata._download.urllib.request.urlopen",
            return_value=FakeResponse(release_payload),
        ):
            with self.assertRaises(CliError):
                download_images_metadata(global_cfg)


def _build_global_config() -> GlobalConfig:
    return GlobalConfig(
        image_registry="ghcr.io",
        image_registry_api_url="https://ghcr.io/v2",
        image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
        image_repository="aicage/aicage",
        default_image_base="ubuntu",
        images_metadata_release_api_url="https://api.github.com/repos/aicage/aicage-image/releases/latest",
        images_metadata_asset_name="images-metadata.yaml",
        images_metadata_download_retries=3,
        images_metadata_retry_backoff_seconds=1.5,
    )
