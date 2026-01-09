from pathlib import Path
from unittest import TestCase, mock

from aicage.config.context import ConfigContext
from aicage.config.global_config import GlobalConfig
from aicage.config.project_config import AgentConfig, ProjectConfig
from aicage.errors import CliError
from aicage.registry._extended_images import ExtendedImageConfig
from aicage.registry.extensions import ExtensionMetadata
from aicage.registry.image_selection.extensions.extended_images import (
    apply_extended_selection,
    load_extended_image_options,
    resolve_extended_image,
)
from aicage.registry.images_metadata.models import AgentMetadata, ImagesMetadata, _ImageReleaseInfo
from aicage.runtime.prompts import ExtendedImageOption


class ExtendedImageSelectionTests(TestCase):
    def test_load_extended_image_options_filters_agent_and_base(self) -> None:
        config = ExtendedImageConfig(
            name="custom",
            agent="codex",
            base="ubuntu",
            extensions=["ext"],
            image_ref="aicage-extended:custom",
            path=Path("/tmp/custom/image-extended.yaml"),
        )
        wrong_base = ExtendedImageConfig(
            name="wrong-base",
            agent="codex",
            base="debian",
            extensions=["ext"],
            image_ref="aicage-extended:wrong-base",
            path=Path("/tmp/wrong/image-extended.yaml"),
        )
        other = ExtendedImageConfig(
            name="other",
            agent="claude",
            base="ubuntu",
            extensions=["ext"],
            image_ref="aicage-extended:other",
            path=Path("/tmp/other/image-extended.yaml"),
        )
        with mock.patch(
            "aicage.registry.image_selection.extensions.extended_images.load_extended_images",
            return_value={"custom": config, "wrong": wrong_base, "other": other},
        ):
            options = load_extended_image_options(
                agent="codex",
                agent_metadata=self._agent_metadata(),
                extensions={"ext": self._extension()},
            )
        self.assertEqual(["custom"], [option.name for option in options])

    def test_resolve_extended_image(self) -> None:
        option = ExtendedImageOption(
            name="custom",
            base="ubuntu",
            description="Custom",
            extensions=["ext"],
            image_ref="aicage-extended:custom",
        )
        self.assertEqual(option, resolve_extended_image("custom", [option]))
        with self.assertRaises(CliError):
            resolve_extended_image("missing", [option])

    def test_apply_extended_selection_updates_config(self) -> None:
        context = self._context()
        agent_cfg = AgentConfig()
        option = ExtendedImageOption(
            name="custom",
            base="ubuntu",
            description="Custom",
            extensions=["ext"],
            image_ref="aicage-extended:custom",
        )
        selection = apply_extended_selection(
            agent="codex",
            agent_cfg=agent_cfg,
            selected=option,
            agent_metadata=self._agent_metadata(),
            context=context,
        )
        self.assertEqual("ubuntu", agent_cfg.base)
        self.assertEqual(["ext"], agent_cfg.extensions)
        self.assertEqual("aicage-extended:custom", agent_cfg.image_ref)
        context.store.save_project.assert_called_once_with(
            Path(context.project_cfg.path),
            context.project_cfg,
        )
        self.assertEqual("aicage-extended:custom", selection.image_ref)

    @staticmethod
    def _extension() -> ExtensionMetadata:
        return ExtensionMetadata(
            extension_id="ext",
            name="Ext",
            description="Desc",
            directory=Path("/tmp/ext"),
            scripts_dir=Path("/tmp/ext/scripts"),
            dockerfile_path=None,
        )

    @staticmethod
    def _agent_metadata() -> AgentMetadata:
        return AgentMetadata(
            agent_path="~/.codex",
            agent_full_name="Codex",
            agent_homepage="https://example.com",
            valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
            local_definition_dir=None,
        )

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
                local_image_repository="aicage",
                agents={},
            ),
            images_metadata=ImagesMetadata(
                aicage_image=_ImageReleaseInfo(version="0.3.3"),
                aicage_image_base=_ImageReleaseInfo(version="0.3.3"),
                bases={},
                agents={},
            ),
        )
