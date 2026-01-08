from pathlib import Path
from unittest import TestCase, mock

from aicage.config.global_config import GlobalConfig
from aicage.config.runtime_config import RunConfig
from aicage.registry.images_metadata.models import ImagesMetadata, _ImageReleaseInfo
from aicage.registry.local_build._extended_plan import should_build_extended
from aicage.registry.local_build._extended_store import ExtendedBuildRecord


class ExtendedPlanTests(TestCase):
    def test_should_build_when_local_image_missing(self) -> None:
        run_config = self._run_config()
        record = self._record(run_config)
        with mock.patch(
            "aicage.registry.local_build._extended_plan.local_image_exists",
            return_value=False,
        ):
            self.assertTrue(
                should_build_extended(
                    run_config=run_config,
                    record=record,
                    base_image_ref=run_config.base_image_ref,
                    extension_hash=record.extension_hash,
                )
            )

    def test_should_build_returns_false_when_layers_unknown(self) -> None:
        run_config = self._run_config()
        record = self._record(run_config)
        with (
            mock.patch(
                "aicage.registry.local_build._extended_plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.local_build._extended_plan.get_local_rootfs_layers",
                return_value=None,
            ),
        ):
            self.assertFalse(
                should_build_extended(
                    run_config=run_config,
                    record=record,
                    base_image_ref=run_config.base_image_ref,
                    extension_hash=record.extension_hash,
                )
            )

    def test_should_build_when_base_layer_missing(self) -> None:
        run_config = self._run_config()
        record = self._record(run_config)
        with (
            mock.patch(
                "aicage.registry.local_build._extended_plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.local_build._extended_plan.get_local_rootfs_layers",
                side_effect=[["layer-a"], ["layer-b"]],
            ),
        ):
            self.assertTrue(
                should_build_extended(
                    run_config=run_config,
                    record=record,
                    base_image_ref=run_config.base_image_ref,
                    extension_hash=record.extension_hash,
                )
            )

    def test_should_build_returns_false_when_final_layers_unknown(self) -> None:
        run_config = self._run_config()
        record = self._record(run_config)
        with (
            mock.patch(
                "aicage.registry.local_build._extended_plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.local_build._extended_plan.get_local_rootfs_layers",
                side_effect=[["layer-a"], None],
            ),
        ):
            self.assertFalse(
                should_build_extended(
                    run_config=run_config,
                    record=record,
                    base_image_ref=run_config.base_image_ref,
                    extension_hash=record.extension_hash,
                )
            )

    @staticmethod
    def _run_config() -> RunConfig:
        global_cfg = GlobalConfig(
            image_registry="ghcr.io",
            image_registry_api_url="https://ghcr.io/v2",
            image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
            image_repository="aicage/aicage",
            image_base_repository="aicage/aicage-image-base",
            default_image_base="ubuntu",
            version_check_image="ghcr.io/aicage/aicage-image-util:agent-version",
            local_image_repository="aicage",
            agents={},
        )
        images_metadata = ImagesMetadata(
            aicage_image=_ImageReleaseInfo(version="0.3.3"),
            aicage_image_base=_ImageReleaseInfo(version="0.3.3"),
            bases={},
            agents={},
        )
        return RunConfig(
            project_path=Path("/tmp/project"),
            agent="codex",
            base="ubuntu",
            image_ref="aicage-extended:codex-ubuntu-extra",
            base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
            extensions=["extra"],
            agent_version=None,
            global_cfg=global_cfg,
            images_metadata=images_metadata,
            project_docker_args="",
            mounts=[],
        )

    @staticmethod
    def _record(run_config: RunConfig) -> ExtendedBuildRecord:
        return ExtendedBuildRecord(
            agent=run_config.agent,
            base=run_config.base,
            image_ref=run_config.image_ref,
            extensions=list(run_config.extensions),
            extension_hash="hash",
            base_image=run_config.base_image_ref,
            built_at="2024-01-01T00:00:00+00:00",
        )
