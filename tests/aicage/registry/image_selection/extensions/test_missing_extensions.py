import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.context import ConfigContext
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.global_config import GlobalConfig
from aicage.config.images_metadata.models import ImagesMetadata, _ImageReleaseInfo
from aicage.config.project_config import AgentConfig, ProjectConfig
from aicage.registry.errors import RegistryError
from aicage.registry.image_selection.extensions.missing_extensions import (
    _find_projects_using_image,
    _load_yaml,
    ensure_extensions_exist,
)


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

    def test_missing_extensions_raises_on_exit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_cfg = AgentConfig(extensions=["extra"], image_ref="aicage:codex-ubuntu")
            context = self._context(tmp_dir, agent_cfg)

            with mock.patch(
                "aicage.registry.image_selection.extensions.missing_extensions.prompt_for_missing_extensions",
                return_value="exit",
            ):
                with self.assertRaises(RegistryError):
                    ensure_extensions_exist(
                        agent="codex",
                        project_config_path=Path(tmp_dir) / "project.yaml",
                        agent_cfg=agent_cfg,
                        extensions={},
                        context=context,
                    )

    def test_missing_extensions_raises_on_invalid_choice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_cfg = AgentConfig(extensions=["extra"], image_ref="aicage:codex-ubuntu")
            context = self._context(tmp_dir, agent_cfg)

            with mock.patch(
                "aicage.registry.image_selection.extensions.missing_extensions.prompt_for_missing_extensions",
                return_value="later",
            ):
                with self.assertRaises(RegistryError):
                    ensure_extensions_exist(
                        agent="codex",
                        project_config_path=Path(tmp_dir) / "project.yaml",
                        agent_cfg=agent_cfg,
                        extensions={},
                        context=context,
                    )

    def test_find_projects_using_image_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = mock.Mock()
            store.projects_dir = Path(tmp_dir)
            matching = Path(tmp_dir) / "one.yaml"
            matching.write_text(
                "\n".join(
                    [
                        "path: /tmp/project",
                        "agents:",
                        "  codex:",
                        "    image_ref: aicage:codex-ubuntu",
                    ]
                ),
                encoding="utf-8",
            )
            (Path(tmp_dir) / "invalid.yaml").write_text("not: [yaml", encoding="utf-8")
            context = self._context(tmp_dir, AgentConfig())
            context.store = store

            matches = _find_projects_using_image(context, "aicage:codex-ubuntu")

            self.assertEqual([("/tmp/project", matching)], matches)

    def test_find_projects_using_image_empty_ref_returns_empty(self) -> None:
        context = self._context("/tmp", AgentConfig())

        matches = _find_projects_using_image(context, "")

        self.assertEqual([], matches)

    def test_find_projects_using_image_skips_non_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = mock.Mock()
            store.projects_dir = Path(tmp_dir)
            (Path(tmp_dir) / "one.yaml").write_text("path: /tmp/project\n", encoding="utf-8")
            context = self._context(tmp_dir, AgentConfig())
            context.store = store
            with mock.patch(
                "aicage.registry.image_selection.extensions.missing_extensions._load_yaml",
                return_value=[],
            ):
                matches = _find_projects_using_image(context, "aicage:codex-ubuntu")

            self.assertEqual([], matches)

    def test_find_projects_using_image_skips_invalid_agents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = mock.Mock()
            store.projects_dir = Path(tmp_dir)
            Path(tmp_dir, "one.yaml").write_text(
                "\n".join(
                    [
                        "path: /tmp/project",
                        "agents:",
                        "  - not-a-mapping",
                    ]
                ),
                encoding="utf-8",
            )
            context = self._context(tmp_dir, AgentConfig())
            context.store = store

            matches = _find_projects_using_image(context, "aicage:codex-ubuntu")

            self.assertEqual([], matches)

    def test_load_yaml_returns_empty_on_non_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "project.yaml"
            path.write_text("- not-a-mapping\n", encoding="utf-8")

            data = _load_yaml(path)

            self.assertEqual({}, data)

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
            extensions={},
        )
