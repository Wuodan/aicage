from pathlib import Path
from unittest import TestCase, mock

from aicage.config.config_store import SettingsStore
from aicage.constants import DEFAULT_EXTENDED_IMAGE_NAME
from aicage.registry.errors import RegistryError
from aicage.registry.image_selection import _fresh_selection
from aicage.registry.image_selection.models import ImageSelection
from aicage.runtime.prompts.image_choice import ExtendedImageOption, ImageChoice

from ._fixtures import build_context


class ImageSelectionFreshTests(TestCase):
    def test_fresh_selection_accepts_extended_choice(self) -> None:
        context = build_context(mock.Mock(spec=SettingsStore), Path("/tmp/project"), bases=["ubuntu"])
        extended = [
            ExtendedImageOption(
                name="custom",
                base="ubuntu",
                description="Custom",
                extensions=["extra"],
                image_ref=f"{DEFAULT_EXTENDED_IMAGE_NAME}:codex-ubuntu-extra",
            )
        ]
        with (
            mock.patch(
                "aicage.registry.image_selection._fresh_selection.load_extended_image_options",
                return_value=extended,
            ),
            mock.patch(
                "aicage.registry.image_selection._fresh_selection.prompt_for_image_choice",
                return_value=ImageChoice(kind="extended", value="custom"),
            ),
            mock.patch(
                "aicage.registry.image_selection._fresh_selection.resolve_extended_image",
                return_value=extended[0],
            ),
            mock.patch(
                "aicage.registry.image_selection._fresh_selection.apply_extended_selection",
                return_value=ImageSelection(
                    image_ref=f"{DEFAULT_EXTENDED_IMAGE_NAME}:codex-ubuntu-extra",
                    base="ubuntu",
                    extensions=["extra"],
                    base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                ),
            ) as apply_mock,
        ):
            selection = _fresh_selection.fresh_selection(
                agent="codex",
                context=context,
                agent_metadata=context.images_metadata.agents["codex"],
                extensions={},
            )
        self.assertEqual(f"{DEFAULT_EXTENDED_IMAGE_NAME}:codex-ubuntu-extra", selection.image_ref)
        apply_mock.assert_called_once()

    def test_fresh_selection_raises_on_empty_bases(self) -> None:
        context = build_context(mock.Mock(spec=SettingsStore), Path("/tmp/project"), bases=["ubuntu"])
        with mock.patch(
            "aicage.registry.image_selection._fresh_selection.available_bases",
            return_value=[],
        ):
            with self.assertRaises(RegistryError):
                _fresh_selection.fresh_selection(
                    agent="codex",
                    context=context,
                    agent_metadata=context.images_metadata.agents["codex"],
                    extensions={},
                )
