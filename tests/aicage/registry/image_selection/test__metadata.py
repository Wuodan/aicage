from pathlib import Path
from unittest import TestCase

from aicage.config.images_metadata.models import AgentMetadata, ImagesMetadata
from aicage.registry._errors import RegistryError
from aicage.registry.image_selection import _metadata


class ImageSelectionMetadataTests(TestCase):
    def test_require_agent_metadata_raises_when_missing(self) -> None:
        metadata = ImagesMetadata(bases={}, agents={})
        with self.assertRaises(RegistryError):
            _metadata.require_agent_metadata("missing", metadata)

    def test_available_bases_sorts_values(self) -> None:
        agent_metadata = AgentMetadata(
            agent_path="~/.agent",
            agent_full_name="Agent",
            agent_homepage="https://example.com",
            build_local=True,
            valid_bases={"ubuntu": "image", "alpine": "image"},
            local_definition_dir=Path("/tmp/agent"),
        )
        self.assertEqual(
            ["alpine", "ubuntu"],
            _metadata.available_bases("agent", agent_metadata),
        )

    def test_validate_base_raises_on_invalid_base(self) -> None:
        agent_metadata = AgentMetadata(
            agent_path="~/.agent",
            agent_full_name="Agent",
            agent_homepage="https://example.com",
            build_local=True,
            valid_bases={"ubuntu": "image"},
            local_definition_dir=Path("/tmp/agent"),
        )
        with self.assertRaises(RegistryError):
            _metadata.validate_base("agent", "alpine", agent_metadata)
