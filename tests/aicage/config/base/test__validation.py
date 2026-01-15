from unittest import TestCase

from aicage.config import ConfigError
from aicage.config.base._validation import validate_base_mapping


class BaseValidationTests(TestCase):
    def test_validate_base_mapping_defaults_build_local(self) -> None:
        payload = validate_base_mapping(
            {
                "from_image": "ubuntu:latest",
                "base_image_distro": "Ubuntu",
                "base_image_description": "Default",
            }
        )
        self.assertFalse(payload["build_local"])

    def test_validate_base_mapping_rejects_missing_required(self) -> None:
        with self.assertRaises(ConfigError):
            validate_base_mapping({"from_image": "ubuntu:latest"})
