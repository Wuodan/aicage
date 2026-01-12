import tempfile
from pathlib import Path
from unittest import TestCase

from aicage.config import ConfigError, _yaml
from aicage.config.custom_agent import _validation
from aicage.config.images_metadata.models import (
    AGENT_FULL_NAME_KEY,
    AGENT_HOMEPAGE_KEY,
    AGENT_PATH_KEY,
    BASE_EXCLUDE_KEY,
    BUILD_LOCAL_KEY,
)


class CustomAgentValidationTests(TestCase):
    def test_ensure_required_files_accepts_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir)
            (agent_dir / "install.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
            (agent_dir / "version.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")

            _validation.ensure_required_files("custom", agent_dir)

    def test_ensure_required_files_requires_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir)
            (agent_dir / "install.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")

            with self.assertRaises(ConfigError):
                _validation.ensure_required_files("custom", agent_dir)

    def test_expect_string_rejects_empty(self) -> None:
        with self.assertRaises(ConfigError):
            _validation.expect_string(" ", AGENT_PATH_KEY)

    def test_expect_bool_rejects_non_bool(self) -> None:
        with self.assertRaises(ConfigError):
            _yaml.expect_bool("true", BUILD_LOCAL_KEY)

    def test_maybe_str_list_rejects_non_string_items(self) -> None:
        with self.assertRaises(ConfigError):
            _yaml.maybe_str_list(["ok", ""], BASE_EXCLUDE_KEY)

    def test_validate_agent_mapping_rejects_missing_required(self) -> None:
        with self.assertRaises(ConfigError):
            _validation.validate_agent_mapping({AGENT_PATH_KEY: "~/.custom"})

    def test_validate_agent_mapping_defaults_build_local(self) -> None:
        payload = _validation.validate_agent_mapping(
            {
                AGENT_PATH_KEY: "~/.custom",
                AGENT_FULL_NAME_KEY: "Custom",
                AGENT_HOMEPAGE_KEY: "https://example.com",
            }
        )
        self.assertTrue(payload[BUILD_LOCAL_KEY])
