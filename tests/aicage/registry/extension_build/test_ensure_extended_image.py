from pathlib import Path
from unittest import TestCase, mock

from aicage.config.extensions import ExtensionMetadata
from aicage.config.global_config import GlobalConfig
from aicage.config.images_metadata.models import AgentMetadata, ImagesMetadata, _ImageReleaseInfo
from aicage.config.runtime_config import RunConfig
from aicage.registry.errors import RegistryError
from aicage.registry.extension_build._extended_store import ExtendedBuildRecord
from aicage.registry.extension_build.ensure_extended_image import ensure_extended_image


class EnsureExtendedImageTests(TestCase):
    def test_ensure_extended_image_raises_without_extensions(self) -> None:
        run_config = self._run_config(extensions=[])
        with self.assertRaises(RegistryError):
            ensure_extended_image(run_config)

    def test_ensure_extended_image_raises_on_missing_extension(self) -> None:
        run_config = self._run_config(extensions=["missing"])
        with mock.patch(
            "aicage.registry.extension_build.ensure_extended_image.load_extensions",
            return_value={},
        ):
            with self.assertRaises(RegistryError):
                ensure_extended_image(run_config)

    def test_ensure_extended_image_skips_when_not_needed(self) -> None:
        run_config = self._run_config(extensions=["ext"], local_definition_dir=None)
        extension = self._extension("ext")
        store = mock.Mock()
        store.load.return_value = None
        with (
            mock.patch(
                "aicage.registry.extension_build.ensure_extended_image.load_extensions",
                return_value={"ext": extension},
            ),
            mock.patch(
                "aicage.registry.extension_build.ensure_extended_image.ExtendedBuildStore",
                return_value=store,
            ),
            mock.patch(
                "aicage.registry.extension_build.ensure_extended_image.extension_hash",
                return_value="hash",
            ),
            mock.patch(
                "aicage.registry.extension_build.ensure_extended_image.should_build_extended",
                return_value=False,
            ),
            mock.patch(
                "aicage.registry.extension_build.ensure_extended_image.run_extended_build"
            ) as run_mock,
        ):
            ensure_extended_image(run_config)
        run_mock.assert_not_called()
        store.save.assert_not_called()

    def test_ensure_extended_image_builds_when_needed(self) -> None:
        run_config = self._run_config(extensions=["ext"], local_definition_dir=Path("/tmp/def"))
        extension = self._extension("ext")
        store = mock.Mock()
        store.load.return_value = None
        with (
            mock.patch(
                "aicage.registry.extension_build.ensure_extended_image.load_extensions",
                return_value={"ext": extension},
            ),
            mock.patch(
                "aicage.registry.extension_build.ensure_extended_image.ExtendedBuildStore",
                return_value=store,
            ),
            mock.patch(
                "aicage.registry.extension_build.ensure_extended_image.extension_hash",
                return_value="hash",
            ),
            mock.patch(
                "aicage.registry.extension_build.ensure_extended_image.should_build_extended",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.extension_build.ensure_extended_image.run_extended_build"
            ) as run_mock,
            mock.patch(
                "aicage.registry.extension_build.ensure_extended_image.build_log_path_for_image",
                return_value=Path("/tmp/logs/build.log"),
            ),
            mock.patch(
                "aicage.registry.extension_build.ensure_extended_image._now_iso",
                return_value="2024-01-01T00:00:00+00:00",
            ),
        ):
            ensure_extended_image(run_config)
        run_mock.assert_called_once()
        store.save.assert_called_once()
        record = store.save.call_args.args[0]
        self.assertIsInstance(record, ExtendedBuildRecord)

    @staticmethod
    def _extension(extension_id: str) -> ExtensionMetadata:
        return ExtensionMetadata(
            extension_id=extension_id,
            name=extension_id,
            description="desc",
            directory=Path("/tmp/ext"),
            scripts_dir=Path("/tmp/ext/scripts"),
            dockerfile_path=None,
        )

    @staticmethod
    def _run_config(
        extensions: list[str],
        local_definition_dir: Path | None = None,
    ) -> RunConfig:
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
            agents={
                "codex": AgentMetadata(
                    agent_path="~/.codex",
                    agent_full_name="Codex",
                    agent_homepage="https://example.com",
                    valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                    local_definition_dir=local_definition_dir,
                )
            },
        )
        return RunConfig(
            project_path=Path("/tmp/project"),
            agent="codex",
            base="ubuntu",
            image_ref="aicage-extended:codex-ubuntu-ext",
            base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
            extensions=extensions,
            global_cfg=global_cfg,
            images_metadata=images_metadata,
            project_docker_args="",
            mounts=[],
        )
