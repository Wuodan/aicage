from pathlib import Path
from unittest import TestCase, mock

from aicage.config.context import ConfigContext
from aicage.config.images_metadata.models import ImagesMetadata, _ImageReleaseInfo
from aicage.config.project_config import ProjectConfig
from aicage.config.runtime_config import RunConfig
from aicage.constants import DEFAULT_EXTENDED_IMAGE_NAME
from aicage.registry.extension_build._extended_plan import should_build_extended
from aicage.registry.extension_build._extended_store import ExtendedBuildRecord
from aicage.registry.image_selection import ImageSelection


class ExtendedPlanTests(TestCase):
    def test_should_build_extended_when_local_image_missing(self) -> None:
        run_config = self._run_config()
        record = self._record(run_config)
        with mock.patch(
            "aicage.registry.extension_build._extended_plan.local_image_exists",
            return_value=False,
        ):
            self.assertTrue(
                should_build_extended(
                    run_config=run_config,
                    record=record,
                    base_image_ref=run_config.selection.base_image_ref,
                    extension_hash=record.extension_hash,
                )
            )

    def test_should_build_extended_returns_false_when_layers_unknown(self) -> None:
        run_config = self._run_config()
        record = self._record(run_config)
        with (
            mock.patch(
                "aicage.registry.extension_build._extended_plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.layers.get_local_rootfs_layers",
                return_value=None,
            ),
        ):
            self.assertFalse(
                should_build_extended(
                    run_config=run_config,
                    record=record,
                    base_image_ref=run_config.selection.base_image_ref,
                    extension_hash=record.extension_hash,
                )
            )

    def test_should_build_extended_when_base_layer_missing(self) -> None:
        run_config = self._run_config()
        record = self._record(run_config)
        with (
            mock.patch(
                "aicage.registry.extension_build._extended_plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.layers.get_local_rootfs_layers",
                side_effect=[["layer-a"], ["layer-b"]],
            ),
        ):
            self.assertTrue(
                should_build_extended(
                    run_config=run_config,
                    record=record,
                    base_image_ref=run_config.selection.base_image_ref,
                    extension_hash=record.extension_hash,
                )
            )

    def test_should_build_extended_returns_false_when_final_layers_unknown(self) -> None:
        run_config = self._run_config()
        record = self._record(run_config)
        with (
            mock.patch(
                "aicage.registry.extension_build._extended_plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.layers.get_local_rootfs_layers",
                side_effect=[["layer-a"], None],
            ),
        ):
            self.assertFalse(
                should_build_extended(
                    run_config=run_config,
                    record=record,
                    base_image_ref=run_config.selection.base_image_ref,
                    extension_hash=record.extension_hash,
                )
            )

    @staticmethod
    def _run_config() -> RunConfig:
        images_metadata = ImagesMetadata(
            aicage_image=_ImageReleaseInfo(version="0.3.3"),
            aicage_image_base=_ImageReleaseInfo(version="0.3.3"),
            bases={},
            agents={},
        )
        return RunConfig(
            project_path=Path("/tmp/project"),
            agent="codex",
            context=ConfigContext(
                store=mock.Mock(),
                project_cfg=ProjectConfig(path="/tmp/project", agents={}),
                images_metadata=images_metadata,
                extensions={},
            ),
            selection=ImageSelection(
                image_ref=f"{DEFAULT_EXTENDED_IMAGE_NAME}:codex-ubuntu-extra",
                base="ubuntu",
                extensions=["extra"],
                base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
            ),
            project_docker_args="",
            mounts=[],
        )

    @staticmethod
    def _record(run_config: RunConfig) -> ExtendedBuildRecord:
        return ExtendedBuildRecord(
            agent=run_config.agent,
            base=run_config.selection.base,
            image_ref=run_config.selection.image_ref,
            extensions=list(run_config.selection.extensions),
            extension_hash="hash",
            base_image=run_config.selection.base_image_ref,
            built_at="2024-01-01T00:00:00+00:00",
        )
