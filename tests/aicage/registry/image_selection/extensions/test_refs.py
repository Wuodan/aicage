from pathlib import Path
from unittest import TestCase, mock

from aicage.config.context import ConfigContext
from aicage.config.images_metadata.models import (
    AgentMetadata,
    BaseMetadata,
    ImagesMetadata,
    _ImageReleaseInfo,
)
from aicage.config.project_config import ProjectConfig
from aicage.constants import LOCAL_IMAGE_REPOSITORY
from aicage.registry.image_selection.extensions.refs import base_image_ref


class ExtensionRefsTests(TestCase):
    def test_base_image_ref_uses_local_repo_for_custom_agent(self) -> None:
        context = self._context()
        agent_metadata = AgentMetadata(
            agent_path="~/.codex",
            agent_full_name="Codex",
            agent_homepage="https://example.com",
            build_local=True,
            valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
            local_definition_dir=Path("/tmp/def"),
        )

        result = base_image_ref(agent_metadata, "codex", "ubuntu", context)

        self.assertEqual(f"{LOCAL_IMAGE_REPOSITORY}:codex-ubuntu", result)

    def test_base_image_ref_uses_remote_for_builtin_agent(self) -> None:
        context = self._context()
        agent_metadata = AgentMetadata(
            agent_path="~/.codex",
            agent_full_name="Codex",
            agent_homepage="https://example.com",
            build_local=False,
            valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
            local_definition_dir=None,
        )

        result = base_image_ref(agent_metadata, "codex", "ubuntu", context)

        self.assertEqual("ghcr.io/aicage/aicage:codex-ubuntu", result)

    def test_base_image_ref_uses_local_for_custom_base(self) -> None:
        context = self._context()
        agent_metadata = AgentMetadata(
            agent_path="~/.codex",
            agent_full_name="Codex",
            agent_homepage="https://example.com",
            build_local=False,
            valid_bases={"custom": "ghcr.io/aicage/aicage:codex-custom"},
            local_definition_dir=None,
        )
        context.custom_bases = {
            "custom": BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro="Ubuntu",
                base_image_description="Custom",
                os_installer="",
                test_suite="",
            )
        }
        result = base_image_ref(agent_metadata, "codex", "custom", context)

        self.assertEqual(f"{LOCAL_IMAGE_REPOSITORY}:codex-custom", result)

    @staticmethod
    def _context() -> ConfigContext:
        return ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path="/tmp/project", agents={}),
            images_metadata=ImagesMetadata(
                aicage_image=_ImageReleaseInfo(version="0.3.3"),
                aicage_image_base=_ImageReleaseInfo(version="0.3.3"),
                bases={},
                agents={},
            ),
            extensions={},
        )
