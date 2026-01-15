from pathlib import Path
from unittest import TestCase, mock

from aicage.config.base.models import BaseMetadata
from aicage.paths import CUSTOM_BASES_DIR
from aicage.registry.local_build import _refs


class LocalBuildRefsTests(TestCase):
    def test_get_base_image_ref_uses_custom_base(self) -> None:
        run_config = mock.Mock()
        run_config.selection = mock.Mock()
        run_config.selection.base = "custom"
        run_config.context = mock.Mock()
        run_config.context.bases = {
            "custom": BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro="Ubuntu",
                base_image_description="Custom",
                build_local=True,
                local_definition_dir=CUSTOM_BASES_DIR / "custom",
            )
        }
        ref = _refs.get_base_image_ref(run_config)

        self.assertEqual("aicage-image-base:custom", ref)

    def test_get_base_image_ref_uses_repository(self) -> None:
        run_config = mock.Mock()
        run_config.selection = mock.Mock()
        run_config.selection.base = "ubuntu"
        run_config.context = mock.Mock()
        run_config.context.bases = {
            "ubuntu": BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro="Ubuntu",
                base_image_description="Default",
                build_local=False,
                local_definition_dir=Path("/tmp/ubuntu"),
            )
        }
        ref = _refs.get_base_image_ref(run_config)

        self.assertEqual("ghcr.io/aicage/aicage-image-base:ubuntu", ref)

    def test_base_repository_includes_registry(self) -> None:
        run_config = mock.Mock()

        repository = _refs.base_repository(run_config)

        self.assertEqual("ghcr.io/aicage/aicage-image-base", repository)
