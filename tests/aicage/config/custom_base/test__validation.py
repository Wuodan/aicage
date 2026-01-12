from unittest import TestCase

from aicage.config import ConfigError
from aicage.config.custom_base import _validation


class CustomBaseValidationTests(TestCase):
    def test_validate_base_mapping_rejects_missing_required(self) -> None:
        with self.assertRaises(ConfigError):
            _validation.validate_base_mapping({"from_image": "ubuntu:latest"})

    def test_validate_base_mapping_rejects_unknown_keys(self) -> None:
        with self.assertRaises(ConfigError):
            _validation.validate_base_mapping(
                {
                    "from_image": "ubuntu:latest",
                    "base_image_distro": "Ubuntu",
                    "base_image_description": "Ubuntu base",
                    "extra": "nope",
                }
            )

    def test_validate_base_mapping_rejects_non_string(self) -> None:
        with self.assertRaises(ConfigError):
            _validation.validate_base_mapping(
                {
                    "from_image": 123,
                    "base_image_distro": "Ubuntu",
                    "base_image_description": "Ubuntu base",
                }
            )
