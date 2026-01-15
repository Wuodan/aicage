from pathlib import Path
from unittest import TestCase, mock

from aicage.config import config_store as config_store_module
from aicage.config.agent import loader as agent_loader_module
from aicage.config.base import loader as base_loader_module
from aicage.config.context import ConfigContext
from aicage.config.extensions import loader as extensions_module
from aicage.config.images_metadata import loader as images_loader_module
from aicage.config.images_metadata.models import (
    AgentMetadata,
    BaseMetadata,
    ImagesMetadata,
)
from aicage.config.project_config import ProjectConfig
from aicage.constants import IMAGE_REGISTRY, IMAGE_REPOSITORY


class ContextTests(TestCase):
    def test_image_repository_ref(self) -> None:
        context = ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path="/work/project", agents={}),
            images_metadata=self._get_images_metadata(),
            agents=self._get_agents(),
            bases=self._get_bases(),
            extensions={},
        )
        self.assertEqual(f"{IMAGE_REGISTRY}/{IMAGE_REPOSITORY}", context.image_repository_ref())

    def test_build_config_context_uses_store(self) -> None:
        project_cfg = ProjectConfig(path="/work/project", agents={})
        with (
            mock.patch("aicage.config.config_store.SettingsStore") as store_cls,
            mock.patch("pathlib.Path.cwd", return_value=Path("/work/project")),
            mock.patch("aicage.config.images_metadata.loader.load_images_metadata") as load_metadata,
            mock.patch("aicage.config.base.loader.load_bases") as load_bases,
            mock.patch("aicage.config.agent.loader.load_agents") as load_agents,
            mock.patch("aicage.config.extensions.loader.load_extensions") as load_extensions,
        ):
            store = store_cls.return_value
            store.load_project.return_value = project_cfg
            load_bases.return_value = self._get_bases()
            load_agents.return_value = self._get_agents()
            load_metadata.return_value = self._get_images_metadata()
            load_extensions.return_value = {}

            context = _build_config_context()

        self.assertEqual(project_cfg, context.project_cfg)
        self.assertEqual(self._get_images_metadata(), context.images_metadata)
        self.assertEqual(self._get_agents(), context.agents)
        self.assertEqual(self._get_bases(), context.bases)
        self.assertEqual({}, context.extensions)
        load_metadata.assert_called_once_with(self._get_bases(), self._get_agents())

    @staticmethod
    def _get_images_metadata() -> ImagesMetadata:
        return ImagesMetadata(
            bases=ContextTests._get_bases(),
            agents=ContextTests._get_agents(),
        )

    @staticmethod
    def _get_bases() -> dict[str, BaseMetadata]:
        return {
            "ubuntu": BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro="Ubuntu",
                base_image_description="Default",
                build_local=False,
                local_definition_dir=Path("/tmp/base"),
            )
        }

    @staticmethod
    def _get_agents() -> dict[str, AgentMetadata]:
        return {
            "codex": AgentMetadata(
                agent_path="~/.codex",
                agent_full_name="Codex CLI",
                agent_homepage="https://example.com",
                build_local=False,
                valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                local_definition_dir=Path("/tmp/agent"),
            )
        }


def _build_config_context() -> ConfigContext:
    store = config_store_module.SettingsStore()
    project_path = Path.cwd().resolve()
    bases = base_loader_module.load_bases()
    agents = agent_loader_module.load_agents(bases)
    images_metadata = images_loader_module.load_images_metadata(bases, agents)
    project_cfg = store.load_project(project_path)
    extensions = extensions_module.load_extensions()
    return ConfigContext(
        store=store,
        project_cfg=project_cfg,
        images_metadata=images_metadata,
        agents=agents,
        bases=bases,
        extensions=extensions,
    )
