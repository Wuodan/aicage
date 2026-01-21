from pathlib import Path
from unittest import TestCase, mock

from aicage.config.agent.models import AgentMetadata
from aicage.config.base.models import BaseMetadata
from aicage.config.context import ConfigContext
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.project_config import ProjectConfig
from aicage.config.runtime_config import RunConfig
from aicage.constants import DEFAULT_EXTENDED_IMAGE_NAME
from aicage.registry._errors import RegistryError
from aicage.registry.extension_build._extended_store import ExtendedBuildRecord
from aicage.registry.extension_build.ensure_extended_image import ensure_extended_image
from aicage.registry.image_selection.models import ImageSelection


class EnsureExtendedImageTests(TestCase):
    def test_ensure_extended_image_raises_without_extensions(self) -> None:
        run_config = self._run_config(extensions=[])
        with self.assertRaises(RegistryError):
            ensure_extended_image(run_config)

    def test_ensure_extended_image_raises_on_missing_extension(self) -> None:
        run_config = self._run_config(extensions=["missing"], available_extensions={})
        with self.assertRaises(RegistryError):
            ensure_extended_image(run_config)

    def test_ensure_extended_image_skips_when_not_needed(self) -> None:
        extension = self._extension("ext")
        run_config = self._run_config(
            extensions=["ext"],
            local_definition_dir=Path("/tmp/def"),
            available_extensions={"ext": extension},
        )
        store = mock.Mock()
        store.load.return_value = None
        with (
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
        extension = self._extension("ext")
        run_config = self._run_config(
            extensions=["ext"],
            build_local=True,
            local_definition_dir=Path("/tmp/def"),
            available_extensions={"ext": extension},
        )
        store = mock.Mock()
        store.load.return_value = None
        with (
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
                "aicage.registry.extension_build.ensure_extended_image.now_iso",
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
        build_local: bool = False,
        local_definition_dir: Path = Path("/tmp/def"),
        available_extensions: dict[str, ExtensionMetadata] | None = None,
    ) -> RunConfig:
        bases = {
            "ubuntu": BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro="Ubuntu",
                base_image_description="Default",
                build_local=False,
                local_definition_dir=Path("/tmp/base"),
            )
        }
        agents = {
            "codex": AgentMetadata(
                agent_path="~/.codex",
                agent_full_name="Codex",
                agent_homepage="https://example.com",
                build_local=build_local,
                valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                local_definition_dir=local_definition_dir,
            )
        }
        return RunConfig(
            project_path=Path("/tmp/project"),
            agent="codex",
            context=ConfigContext(
                store=mock.Mock(),
                project_cfg=ProjectConfig(path="/tmp/project", agents={}),
                agents=agents,
                bases=bases,
                extensions=available_extensions or {},
            ),
            selection=ImageSelection(
                image_ref=f"{DEFAULT_EXTENDED_IMAGE_NAME}:codex-ubuntu-ext",
                base="ubuntu",
                extensions=extensions,
                base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
            ),
            project_docker_args="",
            mounts=[],
            env=[],
        )
