import tempfile
from pathlib import Path
from unittest import TestCase

from aicage.config.errors import ConfigError
from aicage.config.agent._validation import ensure_required_files, validate_agent_mapping
from aicage.config.images_metadata.models import (
    AGENT_FULL_NAME_KEY,
    AGENT_HOMEPAGE_KEY,
    AGENT_PATH_KEY,
    BUILD_LOCAL_KEY,
)


class AgentValidationTests(TestCase):
    def test_validate_agent_mapping_defaults_build_local(self) -> None:
        payload = validate_agent_mapping(
            {
                AGENT_PATH_KEY: "~/.custom",
                AGENT_FULL_NAME_KEY: "Custom",
                AGENT_HOMEPAGE_KEY: "https://example.com",
            }
        )
        self.assertTrue(payload[BUILD_LOCAL_KEY])

    def test_ensure_required_files_requires_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir)
            (agent_dir / "install.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")

            with self.assertRaises(ConfigError):
                ensure_required_files("custom", agent_dir)
