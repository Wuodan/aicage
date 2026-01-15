import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.config_store import SettingsStore
from aicage.config.context import ConfigContext
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.images_metadata.models import ImagesMetadata
from aicage.config.project_config import AgentConfig, ProjectConfig
from aicage.registry.errors import RegistryError
from aicage.registry.image_selection.models import ImageSelection
from aicage.registry.image_selection.selection import select_agent_image

from ._fixtures import build_context, metadata_with_bases


class ImageSelectionTests(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._extensions: dict[str, ExtensionMetadata] = {}

    def test_select_agent_image_uses_existing_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()
            store = mock.Mock(spec=SettingsStore)
            context = build_context(store, project_path, bases=["debian", "ubuntu"])
            context.project_cfg.agents["codex"] = AgentConfig(base="debian")
            selection = select_agent_image("codex", context)

            self.assertEqual("ghcr.io/aicage/aicage:codex-debian", selection.image_ref)
            store.save_project.assert_called_once_with(project_path, context.project_cfg)

    def test_select_agent_image_prompts_and_marks_dirty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()
            store = mock.Mock(spec=SettingsStore)
            context = build_context(store, project_path, bases=["alpine", "ubuntu"])
            with (
                mock.patch(
                    "aicage.config.extended_images.IMAGE_EXTENDED_STATE_DIR",
                    Path(tmp_dir) / "extended-images",
                ),
                mock.patch(
                    "aicage.registry.image_selection._fresh_selection.prompt_for_base",
                    return_value="alpine",
                ),
            ):
                select_agent_image("codex", context)

            self.assertEqual("alpine", context.project_cfg.agents["codex"].base)
            store.save_project.assert_called_once_with(project_path, context.project_cfg)

    def test_select_agent_image_raises_without_bases(self) -> None:
        context = build_context(mock.Mock(spec=SettingsStore), Path("/tmp/project"), bases=[])
        with self.assertRaises(RegistryError):
            select_agent_image("codex", context)

    def test_select_agent_image_raises_on_invalid_base(self) -> None:
        context = build_context(
            mock.Mock(spec=SettingsStore),
            Path("/tmp/project"),
            bases=["ubuntu"],
            agents={"codex": AgentConfig(base="alpine")},
        )
        with self.assertRaises(RegistryError):
            select_agent_image("codex", context)

    def test_select_agent_image_build_local_uses_local_tag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()
            store = mock.Mock(spec=SettingsStore)
            metadata = metadata_with_bases(
                ["ubuntu"],
                agent_name="claude",
                build_local=True,
            )
            context = ConfigContext(
                store=store,
                project_cfg=ProjectConfig(path=str(project_path), agents={}),
                images_metadata=metadata,
                agents=metadata.agents,
                bases=metadata.bases,
                extensions=self._extensions,
            )
            context.project_cfg.agents["claude"] = AgentConfig(base="ubuntu")
            selection = select_agent_image("claude", context)

            self.assertEqual("aicage:claude-ubuntu", selection.image_ref)
            store.save_project.assert_called_once_with(project_path, context.project_cfg)

    @staticmethod
    def test_select_agent_image_uses_fresh_selection_when_image_ref_has_no_base() -> None:
        context = build_context(mock.Mock(spec=SettingsStore), Path("/tmp/project"), bases=["ubuntu"])
        agent_cfg = AgentConfig(image_ref="aicage:codex-ubuntu")
        context.project_cfg.agents["codex"] = agent_cfg
        with mock.patch(
            "aicage.registry.image_selection.selection.fresh_selection",
            return_value=ImageSelection(
                image_ref="aicage:codex-ubuntu",
                base="ubuntu",
                extensions=[],
                base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
            ),
        ) as fresh_mock:
            select_agent_image("codex", context)
        fresh_mock.assert_called_once()

    @staticmethod
    def test_select_agent_image_resets_on_missing_extensions() -> None:
        context = build_context(mock.Mock(spec=SettingsStore), Path("/tmp/project"), bases=["ubuntu"])
        agent_cfg = AgentConfig(base="ubuntu", image_ref="aicage:codex-ubuntu", extensions=["extra"])
        context.project_cfg.agents["codex"] = agent_cfg
        with (
            mock.patch(
                "aicage.registry.image_selection.selection.ensure_extensions_exist",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.image_selection.selection.fresh_selection",
                return_value=ImageSelection(
                    image_ref="aicage:codex-ubuntu",
                    base="ubuntu",
                    extensions=[],
                    base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                ),
            ) as fresh_mock,
        ):
            select_agent_image("codex", context)
        fresh_mock.assert_called_once()

    def test_select_agent_image_uses_stored_image_ref(self) -> None:
        context = build_context(mock.Mock(spec=SettingsStore), Path("/tmp/project"), bases=["ubuntu"])
        agent_cfg = AgentConfig(base="ubuntu", image_ref="aicage:codex-ubuntu", extensions=[])
        context.project_cfg.agents["codex"] = agent_cfg
        selection = select_agent_image("codex", context)
        self.assertEqual("aicage:codex-ubuntu", selection.image_ref)

    def test_select_agent_image_raises_when_agent_missing(self) -> None:
        context = ConfigContext(
            store=mock.Mock(spec=SettingsStore),
            project_cfg=ProjectConfig(path="/tmp/project", agents={}),
            images_metadata=ImagesMetadata(
                bases={},
                agents={},
            ),
            agents={},
            bases={},
            extensions=self._extensions,
        )
        with self.assertRaises(RegistryError):
            select_agent_image("codex", context)
