from pathlib import Path
from unittest import TestCase, mock

from aicage.config.agent.models import AgentMetadata
from aicage.config.base.filter import filter_bases
from aicage.config.base.models import BaseMetadata
from aicage.config.context import ConfigContext
from aicage.config.project_config import ProjectConfig


class BaseFilterTests(TestCase):
    def test_filter_bases_excludes_by_name(self) -> None:
        context = self._context()
        agent_metadata = self._agent_metadata(base_exclude=["alpine"])

        filtered = filter_bases(context, agent_metadata)

        self.assertEqual({"ubuntu"}, filtered)

    def test_filter_bases_excludes_by_distro(self) -> None:
        context = self._context()
        agent_metadata = self._agent_metadata(base_distro_exclude=["ubuntu"])

        filtered = filter_bases(context, agent_metadata)

        self.assertEqual({"alpine"}, filtered)

    @staticmethod
    def _context() -> ConfigContext:
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
        return ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path="/tmp/project", agents={}),
            agents={},
            bases=bases,
            extensions={},
        )

    @staticmethod
    def _agent_metadata(
        base_exclude: list[str] | None = None,
        base_distro_exclude: list[str] | None = None,
    ) -> AgentMetadata:
        return AgentMetadata(
            agent_path="~/.agent",
            agent_full_name="Agent",
            agent_homepage="https://example.com",
            build_local=True,
            valid_bases={},
            local_definition_dir=Path("/tmp/agent"),
            base_exclude=base_exclude or [],
            base_distro_exclude=base_distro_exclude or [],
        )
