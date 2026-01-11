from unittest import TestCase

from aicage.config import ConfigError, _extension_validation


class ExtensionValidationTests(TestCase):
    def test_validate_extension_mapping_rejects_non_mapping(self) -> None:
        with self.assertRaises(ConfigError):
            _extension_validation.validate_extension_mapping(["name", "description"])

    def test_validate_extension_mapping_rejects_missing_required(self) -> None:
        with self.assertRaises(ConfigError):
            _extension_validation.validate_extension_mapping({"name": "Example"})

    def test_validate_extension_mapping_rejects_unknown_keys(self) -> None:
        with self.assertRaises(ConfigError):
            _extension_validation.validate_extension_mapping(
                {"name": "Example", "description": "Demo", "extra": "nope"}
            )

    def test_validate_extension_mapping_rejects_empty_strings(self) -> None:
        with self.assertRaises(ConfigError):
            _extension_validation.validate_extension_mapping({"name": " ", "description": "Demo"})

    def test_validate_extension_mapping_accepts_valid_payload(self) -> None:
        payload = _extension_validation.validate_extension_mapping(
            {"name": "Example", "description": "Demo"}
        )
        self.assertEqual(payload, {"name": "Example", "description": "Demo"})
