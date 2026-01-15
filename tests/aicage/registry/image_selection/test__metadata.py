from pathlib import Path
from unittest import TestCase, mock

from aicage.config.context import ConfigContext
from aicage.config.images_metadata.models import AgentMetadata, BaseMetadata, ImagesMetadata
from aicage.config.project_config import ProjectConfig
from aicage.registry._errors import RegistryError
from aicage.registry.image_selection import _metadata


class ImageSelectionMetadataTests(TestCase):
    def test_require_agent_metadata_raises_when_missing(self) -> None:
        with self.assertRaises(RegistryError):
            _metadata.require_agent_metadata("missing", self._context({}, {}))

    def test_available_bases_sorts_values(self) -> None:
        agent_metadata = AgentMetadata(
            agent_path="~/.agent",
            agent_full_name="Agent",
            agent_homepage="https://example.com",
            build_local=True,
            valid_bases={"ubuntu": "image", "alpine": "image"},
            local_definition_dir=Path("/tmp/agent"),
        )
        bases = self._bases()
        context = self._context(bases, {"agent": agent_metadata})
        self.assertEqual(
            ["alpine", "ubuntu"],
            _metadata.available_bases("agent", context),
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
        bases = {"ubuntu": self._bases()["ubuntu"]}
        context = self._context(bases, {"agent": agent_metadata})
        with self.assertRaises(RegistryError):
            _metadata.validate_base("agent", "alpine", context)

    @staticmethod
    def _bases() -> dict[str, BaseMetadata]:
        return {
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

    @staticmethod
    def _context(
        bases: dict[str, BaseMetadata],
        agents: dict[str, AgentMetadata],
    ) -> ConfigContext:
        return ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path="/tmp/project", agents={}),
            images_metadata=ImagesMetadata(bases=bases, agents=agents),
            agents=agents,
            bases=bases,
            extensions={},
        )
