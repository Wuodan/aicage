import tempfile
from pathlib import Path
from unittest import TestCase

from aicage.config.images_metadata.models import (
    _AGENT_KEY,
    _AICAGE_IMAGE_BASE_KEY,
    _AICAGE_IMAGE_KEY,
    _BASE_IMAGE_DESCRIPTION_KEY,
    _BASE_IMAGE_DISTRO_KEY,
    _BASES_KEY,
    _FROM_IMAGE_KEY,
    _VALID_BASES_KEY,
    _VERSION_KEY,
    AGENT_FULL_NAME_KEY,
    AGENT_HOMEPAGE_KEY,
    AGENT_PATH_KEY,
    BUILD_LOCAL_KEY,
    ImagesMetadata,
)
from aicage.runtime.agent_config import resolve_agent_config
from aicage.runtime.errors import RuntimeExecutionError


class AgentConfigTests(TestCase):
    def test_resolve_agent_config_reads_metadata_and_creates_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir) / ".codex"
            metadata = ImagesMetadata.from_mapping(
                {
                    _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
                    _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
                    _BASES_KEY: {
                        "ubuntu": {
                            _FROM_IMAGE_KEY: "ubuntu:latest",
                            _BASE_IMAGE_DISTRO_KEY: "Ubuntu",
                            _BASE_IMAGE_DESCRIPTION_KEY: "Default",
                        }
                    },
                    _AGENT_KEY: {
                        "codex": {
                            AGENT_PATH_KEY: str(agent_dir),
                            AGENT_FULL_NAME_KEY: "Codex CLI",
                            AGENT_HOMEPAGE_KEY: "https://example.com",
                            BUILD_LOCAL_KEY: False,
                            _VALID_BASES_KEY: {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                        }
                    },
                }
            )
            config = resolve_agent_config("codex", metadata)
            self.assertEqual(str(agent_dir), config.agent_path)
            self.assertTrue(config.agent_config_host.exists())

    def test_resolve_agent_config_missing_agent_raises(self) -> None:
        metadata = ImagesMetadata.from_mapping(
            {
                _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
                _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
                _BASES_KEY: {},
                _AGENT_KEY: {},
            }
        )
        with self.assertRaises(RuntimeExecutionError):
            resolve_agent_config("codex", metadata)
