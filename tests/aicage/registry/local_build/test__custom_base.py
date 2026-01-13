import tempfile
from pathlib import Path
from unittest import TestCase, mock

import yaml

from aicage.config.images_metadata.models import BaseMetadata
from aicage.docker.errors import DockerError
from aicage.registry.local_build import _custom_base
from aicage.registry.local_build._custom_base_store import (
    CustomBaseBuildRecord,
    CustomBaseBuildStore,
)


class CustomBaseBuildTests(TestCase):
    def test_custom_base_image_ref_uses_base(self) -> None:
        self.assertEqual("aicage-image-base:custom", _custom_base.custom_base_image_ref("custom"))

    def test_ensure_custom_base_image_builds_when_missing(self) -> None:
        base_metadata = self._base_metadata()
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir) / "custom"
            base_dir.mkdir()
            (base_dir / "Dockerfile").write_text("FROM ${FROM_IMAGE}\n", encoding="utf-8")
            state_dir = Path(tmp_dir) / "state"
            with (
                mock.patch(
                    "aicage.registry.local_build._custom_base_store.BASE_IMAGE_BUILD_STATE_DIR",
                    state_dir,
                ),
                mock.patch(
                    "aicage.registry.local_build._custom_base.local_image_exists",
                    return_value=False,
                ),
                mock.patch(
                    "aicage.registry.local_build._custom_base.get_remote_digest",
                    return_value="sha256:remote",
                ),
                mock.patch(
                    "aicage.registry.local_build._custom_base.run_custom_base_build"
                ) as build_mock,
            ):
                _custom_base.ensure_custom_base_image("custom", base_metadata, base_dir)

            build_mock.assert_called_once()
            record_path = state_dir / "base-custom.yaml"
            payload = yaml.safe_load(record_path.read_text(encoding="utf-8"))
            self.assertEqual("custom", payload["base"])
            self.assertEqual("sha256:remote", payload["from_image_digest"])

    def test_ensure_custom_base_image_skips_when_digest_matches(self) -> None:
        base_metadata = self._base_metadata()
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir) / "custom"
            base_dir.mkdir()
            (base_dir / "Dockerfile").write_text("FROM ${FROM_IMAGE}\n", encoding="utf-8")
            state_dir = Path(tmp_dir) / "state"
            store = CustomBaseBuildStore(state_dir)
            store.save(
                CustomBaseBuildRecord(
                    base="custom",
                    from_image=base_metadata.from_image,
                    from_image_digest="sha256:remote",
                    image_ref=_custom_base.custom_base_image_ref("custom"),
                    built_at="2024-01-01T00:00:00+00:00",
                )
            )
            with (
                mock.patch(
                    "aicage.registry.local_build._custom_base_store.BASE_IMAGE_BUILD_STATE_DIR",
                    state_dir,
                ),
                mock.patch(
                    "aicage.registry.local_build._custom_base.local_image_exists",
                    return_value=True,
                ),
                mock.patch(
                    "aicage.registry.local_build._custom_base.get_remote_digest",
                    return_value="sha256:remote",
                ),
                mock.patch(
                    "aicage.registry.local_build._custom_base.run_custom_base_build"
                ) as build_mock,
            ):
                _custom_base.ensure_custom_base_image("custom", base_metadata, base_dir)

            build_mock.assert_not_called()

    def test_ensure_custom_base_image_warns_on_build_failure(self) -> None:
        base_metadata = self._base_metadata()
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir) / "custom"
            base_dir.mkdir()
            (base_dir / "Dockerfile").write_text("FROM ${FROM_IMAGE}\n", encoding="utf-8")
            state_dir = Path(tmp_dir) / "state"
            with (
                mock.patch(
                    "aicage.registry.local_build._custom_base_store.BASE_IMAGE_BUILD_STATE_DIR",
                    state_dir,
                ),
                mock.patch(
                    "aicage.registry.local_build._custom_base.local_image_exists",
                    return_value=True,
                ),
                mock.patch(
                    "aicage.registry.local_build._custom_base.get_remote_digest",
                    return_value="sha256:remote",
                ),
                mock.patch(
                    "aicage.registry.local_build._custom_base.run_custom_base_build",
                    side_effect=DockerError("build failed"),
                ),
            ):
                _custom_base.ensure_custom_base_image("custom", base_metadata, base_dir)

    @staticmethod
    def _base_metadata() -> BaseMetadata:
        return BaseMetadata(
            from_image="ubuntu:latest",
            base_image_distro="Ubuntu",
            base_image_description="Custom",
            os_installer="",
            test_suite="",
        )
