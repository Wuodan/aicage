from pathlib import Path
from unittest import TestCase

from aicage.config.images_metadata.loader import load_images_metadata
from aicage.config.images_metadata.models import AgentMetadata, BaseMetadata


class ImagesMetadataLoaderTests(TestCase):
    def test_load_images_metadata_returns_inputs(self) -> None:
        bases = {
            "ubuntu": BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro="Ubuntu",
                base_image_description="Good default",
                build_local=False,
                local_definition_dir=Path("/tmp/base"),
            )
        }
        agents = {
            "codex": AgentMetadata(
                agent_path="~/.codex",
                agent_full_name="Codex CLI",
                agent_homepage="https://example.com",
                build_local=False,
                valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                local_definition_dir=Path("/tmp/agent"),
            )
        }
        metadata = load_images_metadata(bases, agents)
        self.assertEqual(bases, metadata.bases)
        self.assertEqual(agents, metadata.agents)
