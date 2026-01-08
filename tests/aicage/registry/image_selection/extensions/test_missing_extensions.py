import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.context import ConfigContext
from aicage.config.global_config import GlobalConfig
from aicage.config.project_config import AgentConfig, ProjectConfig
from aicage.registry._extensions import ExtensionMetadata
from aicage.registry.image_selection.extensions.missing_extensions import ensure_extensions_exist
from aicage.registry.images_metadata.models import ImagesMetadata, _ImageReleaseInfo


class MissingExtensionsTests(TestCase):
    def test_missing_extensions_returns_false_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension = ExtensionMetadata(
                extension_id="extra",
                name="Extra",
                description="Extra tools",
                directory=Path(tmp_dir),
                scripts_dir=Path(tmp_dir),
                dockerfile_path=None,
            )
            agent_cfg = AgentConfig(extensions=["extra"], image_ref="aicage:codex-ubuntu")
            context = self._context(tmp_dir, agent_cfg)

            with mock.patch(
                "aicage.registry.image_selection.extensions.missing_extensions.prompt_for_missing_extensions"
            ) as prompt_mock:
                result = ensure_extensions_exist(
                    agent="codex",
                    project_config_path=Path(tmp_dir) / "project.yaml",
                    agent_cfg=agent_cfg,
                    extensions={"extra": extension},
                    context=context,
                )

            self.assertFalse(result)
            prompt_mock.assert_not_called()

    def test_missing_extensions_resets_on_fresh_choice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_cfg = AgentConfig(extensions=["extra"], image_ref="aicage:codex-ubuntu")
            context = self._context(tmp_dir, agent_cfg)

            with mock.patch(
                "aicage.registry.image_selection.extensions.missing_extensions.prompt_for_missing_extensions",
                return_value="fresh",
            ):
                result = ensure_extensions_exist(
                    agent="codex",
                    project_config_path=Path(tmp_dir) / "project.yaml",
                    agent_cfg=agent_cfg,
                    extensions={},
                    context=context,
                )

            self.assertTrue(result)
            self.assertNotIn("codex", context.project_cfg.agents)
            context.store.save_project.assert_called_once_with(
                Path(context.project_cfg.path),
                context.project_cfg,
            )

    @staticmethod
    def _context(tmp_dir: str, agent_cfg: AgentConfig) -> ConfigContext:
        store = mock.Mock()
        store.projects_dir = Path(tmp_dir)
        project_cfg = ProjectConfig(path=str(Path(tmp_dir) / "project"), agents={"codex": agent_cfg})
        return ConfigContext(
            store=store,
            project_cfg=project_cfg,
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
