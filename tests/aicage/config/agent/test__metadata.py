from pathlib import Path
from unittest import TestCase

from aicage.config.agent._metadata import build_agent_metadata
from aicage.config.images_metadata.models import (
    AGENT_FULL_NAME_KEY,
    AGENT_HOMEPAGE_KEY,
    AGENT_PATH_KEY,
    BASE_EXCLUDE_KEY,
    BUILD_LOCAL_KEY,
    BaseMetadata,
)


class AgentMetadataBuilderTests(TestCase):
    def test_build_agent_metadata_filters_bases_and_sets_refs(self) -> None:
        bases = {
            "ubuntu": BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro="Ubuntu",
                base_image_description="Default",
                build_local=False,
                local_definition_dir=Path("/tmp/ubuntu"),
            ),
            "alpine": BaseMetadata(
                from_image="alpine:latest",
                base_image_distro="Alpine",
                base_image_description="Minimal",
                build_local=False,
                local_definition_dir=Path("/tmp/alpine"),
            ),
        }
        mapping = {
            AGENT_PATH_KEY: "~/.codex",
            AGENT_FULL_NAME_KEY: "Codex",
            AGENT_HOMEPAGE_KEY: "https://example.com",
            BUILD_LOCAL_KEY: False,
            BASE_EXCLUDE_KEY: ["alpine"],
        }

        metadata = build_agent_metadata(
            agent_name="codex",
            agent_mapping=mapping,
            bases=bases,
            definition_dir=Path("/tmp/agent"),
        )

        self.assertEqual(
            {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
            metadata.valid_bases,
        )
