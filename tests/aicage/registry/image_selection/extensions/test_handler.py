import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.context import ConfigContext
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.global_config import GlobalConfig
from aicage.config.images_metadata.models import AgentMetadata, ImagesMetadata, _BaseMetadata, _ImageReleaseInfo
from aicage.config.project_config import AgentConfig, ProjectConfig
from aicage.registry.image_selection.extensions.context import ExtensionSelectionContext
from aicage.registry.image_selection.extensions.handler import handle_extension_selection


class ExtensionHandlerTests(TestCase):
    def test_handle_extension_selection_uses_base_when_none_selected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            context = self._context(tmp_dir)
            agent_cfg = AgentConfig()
            selection = ExtensionSelectionContext(
                agent="codex",
                base="ubuntu",
                agent_cfg=agent_cfg,
                agent_metadata=self._agent_metadata(local=False),
                extensions={},
                context=context,
            )
            with mock.patch(
                "aicage.registry.image_selection.extensions.handler.prompt_for_extensions",
                return_value=[],
            ):
                result = handle_extension_selection(selection)

            self.assertEqual("ghcr.io/aicage/aicage:codex-ubuntu", result.image_ref)
            self.assertEqual([], agent_cfg.extensions)
            context.store.save_project.assert_called_once()

    def test_handle_extension_selection_persists_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            context = self._context(tmp_dir)
            agent_cfg = AgentConfig()
            extension = self._extension(tmp_dir, "extra")
            selection = ExtensionSelectionContext(
                agent="codex",
                base="ubuntu",
                agent_cfg=agent_cfg,
                agent_metadata=self._agent_metadata(local=False),
                extensions={"extra": extension},
                context=context,
            )
            with (
                mock.patch(
                    "aicage.registry.image_selection.extensions.handler.prompt_for_extensions",
                    return_value=["extra"],
                ),
                mock.patch(
                    "aicage.registry.image_selection.extensions.handler.prompt_for_image_ref",
                    return_value="aicage-extended:custom",
                ),
                mock.patch(
                    "aicage.registry.image_selection.extensions.handler.write_extended_image_config"
                ) as write_mock,
            ):
                result = handle_extension_selection(selection)

            self.assertEqual("aicage-extended:custom", result.image_ref)
            self.assertEqual(["extra"], agent_cfg.extensions)
            write_mock.assert_called_once()
            context.store.save_project.assert_called_once()

    @staticmethod
    def _extension(tmp_dir: str, extension_id: str) -> ExtensionMetadata:
        base = Path(tmp_dir)
        return ExtensionMetadata(
            extension_id=extension_id,
            name=extension_id,
            description="desc",
            directory=base,
            scripts_dir=base,
            dockerfile_path=None,
        )

    @staticmethod
    def _agent_metadata(local: bool) -> AgentMetadata:
        return AgentMetadata(
            agent_path="~/.codex",
            agent_full_name="Codex",
            agent_homepage="https://example.com",
            build_local=local,
            valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
            local_definition_dir=Path("/tmp/def") if local else None,
        )

    @staticmethod
    def _context(tmp_dir: str) -> ConfigContext:
        return ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path=str(Path(tmp_dir) / "project"), agents={}),
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
                bases={
                    "ubuntu": _BaseMetadata(
                        from_image="ubuntu:latest",
                        base_image_distro="Ubuntu",
                        base_image_description="Default",
                        os_installer="distro/debian/install.sh",
                        test_suite="default",
                    )
                },
                agents={},
            ),
            extensions={},
        )
