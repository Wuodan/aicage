import tempfile
from pathlib import Path
from unittest import TestCase

from aicage.config.images_metadata.models import (
    AgentMetadata,
    BaseMetadata,
    ImagesMetadata,
)
from aicage.runtime.agent_config import resolve_agent_config
from aicage.runtime.errors import RuntimeExecutionError


class AgentConfigTests(TestCase):
    def test_resolve_agent_config_reads_metadata_and_creates_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir) / ".codex"
            metadata = ImagesMetadata(
                bases={
                    "ubuntu": BaseMetadata(
                        from_image="ubuntu:latest",
                        base_image_distro="Ubuntu",
                        base_image_description="Default",
                        build_local=False,
                        local_definition_dir=Path("/tmp/base"),
                    )
                },
                agents={
                    "codex": AgentMetadata(
                        agent_path=str(agent_dir),
                        agent_full_name="Codex CLI",
                        agent_homepage="https://example.com",
                        build_local=False,
                        valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                        local_definition_dir=Path("/tmp/agent"),
                    )
                },
            )
            config = resolve_agent_config("codex", metadata)
            self.assertEqual(str(agent_dir), config.agent_path)
            self.assertTrue(config.agent_config_host.exists())

    def test_resolve_agent_config_missing_agent_raises(self) -> None:
        metadata = ImagesMetadata(bases={}, agents={})
        with self.assertRaises(RuntimeExecutionError):
            resolve_agent_config("codex", metadata)
