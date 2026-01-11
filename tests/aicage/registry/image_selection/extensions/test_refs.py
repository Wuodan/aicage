from pathlib import Path
from unittest import TestCase, mock

from aicage.config.context import ConfigContext
from aicage.config.global_config import GlobalConfig
from aicage.config.images_metadata.models import AgentMetadata, ImagesMetadata, _ImageReleaseInfo
from aicage.config.project_config import ProjectConfig
from aicage.registry.image_selection.extensions.refs import base_image_ref


class ExtensionRefsTests(TestCase):
    def test_base_image_ref_uses_local_repo_for_custom_agent(self) -> None:
        context = self._context()
        agent_metadata = AgentMetadata(
            agent_path="~/.codex",
            agent_full_name="Codex",
            agent_homepage="https://example.com",
            valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
            local_definition_dir=Path("/tmp/def"),
        )

        result = base_image_ref(agent_metadata, "codex", "ubuntu", context)

        self.assertEqual("local:codex-ubuntu", result)

    def test_base_image_ref_uses_remote_for_builtin_agent(self) -> None:
        context = self._context()
        agent_metadata = AgentMetadata(
            agent_path="~/.codex",
            agent_full_name="Codex",
            agent_homepage="https://example.com",
            valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
            local_definition_dir=None,
        )

        result = base_image_ref(agent_metadata, "codex", "ubuntu", context)

        self.assertEqual("ghcr.io/aicage/aicage:codex-ubuntu", result)

    @staticmethod
    def _context() -> ConfigContext:
        return ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path="/tmp/project", agents={}),
            global_cfg=GlobalConfig(
                image_registry="ghcr.io",
                image_registry_api_url="https://ghcr.io/v2",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                image_repository="aicage/aicage",
                image_base_repository="aicage/aicage-image-base",
                default_image_base="ubuntu",
                version_check_image="ghcr.io/aicage/aicage-image-util:agent-version",
                local_image_repository="local",
                agents={},
            ),
            images_metadata=ImagesMetadata(
                aicage_image=_ImageReleaseInfo(version="0.3.3"),
                aicage_image_base=_ImageReleaseInfo(version="0.3.3"),
                bases={},
                agents={},
            ),
            extensions={},
        )
