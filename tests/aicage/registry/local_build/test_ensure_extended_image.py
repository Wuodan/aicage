from pathlib import Path
from unittest import TestCase, mock

from aicage.config.global_config import GlobalConfig
from aicage.config.runtime_config import RunConfig
from aicage.errors import CliError
from aicage.registry.extensions import ExtensionMetadata
from aicage.registry.images_metadata.models import AgentMetadata, ImagesMetadata, _ImageReleaseInfo
from aicage.registry.local_build._extended_store import ExtendedBuildRecord
from aicage.registry.local_build.ensure_extended_image import ensure_extended_image


class EnsureExtendedImageTests(TestCase):
    def test_ensure_extended_image_raises_without_extensions(self) -> None:
        run_config = self._run_config(extensions=[])
        with self.assertRaises(CliError):
            ensure_extended_image(run_config)

    def test_ensure_extended_image_raises_on_missing_extension(self) -> None:
        run_config = self._run_config(extensions=["missing"])
        with mock.patch("aicage.registry.local_build.ensure_extended_image.load_extensions", return_value={}):
            with self.assertRaises(CliError):
                ensure_extended_image(run_config)

    def test_ensure_extended_image_pulls_for_builtin_agent(self) -> None:
        run_config = self._run_config(extensions=["ext"], local_definition_dir=None)
        extension = self._extension("ext")
        store = mock.Mock()
        store.load.return_value = None
        with (
            mock.patch(
                "aicage.registry.local_build.ensure_extended_image.load_extensions",
                return_value={"ext": extension},
            ),
            mock.patch(
                "aicage.registry.local_build.ensure_extended_image.ExtendedBuildStore",
                return_value=store,
            ),
            mock.patch(
                "aicage.registry.local_build.ensure_extended_image.extension_hash",
                return_value="hash",
            ),
            mock.patch(
                "aicage.registry.local_build.ensure_extended_image.pull_image"
            ) as pull_mock,
            mock.patch(
                "aicage.registry.local_build.ensure_extended_image.should_build_extended",
                return_value=False,
            ),
        ):
            ensure_extended_image(run_config)
        pull_mock.assert_called_once()

    def test_ensure_extended_image_builds_when_needed(self) -> None:
        run_config = self._run_config(extensions=["ext"], local_definition_dir=Path("/tmp/def"))
        extension = self._extension("ext")
        store = mock.Mock()
        store.load.return_value = None
        with (
            mock.patch(
                "aicage.registry.local_build.ensure_extended_image.load_extensions",
                return_value={"ext": extension},
            ),
            mock.patch(
                "aicage.registry.local_build.ensure_extended_image.ExtendedBuildStore",
                return_value=store,
            ),
            mock.patch(
                "aicage.registry.local_build.ensure_extended_image.extension_hash",
                return_value="hash",
            ),
            mock.patch(
                "aicage.registry.local_build.ensure_extended_image.ensure_local_image"
            ) as ensure_local_mock,
            mock.patch(
                "aicage.registry.local_build.ensure_extended_image.should_build_extended",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.local_build.ensure_extended_image.run_extended_build"
            ) as run_mock,
            mock.patch(
                "aicage.registry.local_build.ensure_extended_image.build_log_path_for_image",
                return_value=Path("/tmp/logs/build.log"),
            ),
            mock.patch(
                "aicage.registry.local_build.ensure_extended_image.now_iso",
                return_value="2024-01-01T00:00:00+00:00",
            ),
        ):
            ensure_extended_image(run_config)
        ensure_local_mock.assert_called_once()
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
            agent_version=None,
            global_cfg=global_cfg,
            images_metadata=images_metadata,
            project_docker_args="",
            mounts=[],
        )
