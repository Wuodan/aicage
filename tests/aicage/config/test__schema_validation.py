from unittest import TestCase

from aicage.config._schema_validation import validate_schema_mapping
from aicage.config.errors import ConfigError


class SchemaValidationTests(TestCase):
    def test_validate_schema_mapping_applies_normalizer_and_validator(self) -> None:
        schema = {
            "properties": {"name": {"type": "string"}, "enabled": {"type": "boolean"}},
            "required": ["name"],
            "additionalProperties": False,
        }

        def normalizer(mapping: dict[str, object]) -> dict[str, object]:
            payload = dict(mapping)
            payload.setdefault("enabled", True)
            return payload

        def validator(value: object, schema_entry: dict[str, object], context: str) -> None:
            if schema_entry.get("type") == "string" and not isinstance(value, str):
                raise ConfigError(f"{context} must be a string.")
            if schema_entry.get("type") == "boolean" and not isinstance(value, bool):
                raise ConfigError(f"{context} must be a boolean.")

        payload = validate_schema_mapping(
            {"name": "agent"},
            schema,
            "example",
            normalizer=normalizer,
            value_validator=validator,
        )

        self.assertEqual({"name": "agent", "enabled": True}, payload)

    def test_validate_schema_mapping_rejects_missing_keys(self) -> None:
        schema = {"properties": {"name": {"type": "string"}}, "required": ["name"]}
        with self.assertRaises(ConfigError):
            validate_schema_mapping({}, schema, "example")

    def test_validate_schema_mapping_rejects_unknown_keys(self) -> None:
        schema = {"properties": {"name": {"type": "string"}}, "required": [], "additionalProperties": False}
        with self.assertRaises(ConfigError):
            validate_schema_mapping({"name": "agent", "extra": "value"}, schema, "example")
