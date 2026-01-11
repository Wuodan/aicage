from pathlib import Path
from unittest import TestCase, mock

from aicage.config import config_store as config_store_module
from aicage.config.context import ConfigContext
from aicage.config.extensions import loader as extensions_module
from aicage.config.global_config import GlobalConfig
from aicage.config.images_metadata import loader as images_loader_module
from aicage.config.images_metadata.models import (
    _AGENT_KEY,
    _AICAGE_IMAGE_BASE_KEY,
    _AICAGE_IMAGE_KEY,
    _BASE_IMAGE_DESCRIPTION_KEY,
    _BASE_IMAGE_DISTRO_KEY,
    _BASES_KEY,
    _FROM_IMAGE_KEY,
    _OS_INSTALLER_KEY,
    _TEST_SUITE_KEY,
    _VALID_BASES_KEY,
    _VERSION_KEY,
    AGENT_FULL_NAME_KEY,
    AGENT_HOMEPAGE_KEY,
    AGENT_PATH_KEY,
    BUILD_LOCAL_KEY,
    ImagesMetadata,
)
from aicage.config.project_config import ProjectConfig


class ContextTests(TestCase):
    def test_image_repository_ref(self) -> None:
        context = ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path="/work/project", agents={}),
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
            images_metadata=self._get_images_metadata(),
            extensions={},
        )
        self.assertEqual("ghcr.io/aicage/aicage", context.image_repository_ref())

    def test_build_config_context_uses_store(self) -> None:
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
        project_cfg = ProjectConfig(path="/work/project", agents={})
        with (
            mock.patch("aicage.config.config_store.SettingsStore") as store_cls,
            mock.patch("pathlib.Path.cwd", return_value=Path("/work/project")),
            mock.patch("aicage.config.images_metadata.loader.load_images_metadata") as load_metadata,
            mock.patch("aicage.config.extensions.loader.load_extensions") as load_extensions,
        ):
            store = store_cls.return_value
            store.load_global.return_value = global_cfg
            store.load_project.return_value = project_cfg
            load_metadata.return_value = self._get_images_metadata()
            load_extensions.return_value = {}

            context = _build_config_context()

        self.assertEqual(global_cfg, context.global_cfg)
        self.assertEqual(project_cfg, context.project_cfg)
        self.assertEqual(self._get_images_metadata(), context.images_metadata)
        self.assertEqual({}, context.extensions)
        load_metadata.assert_called_once_with("aicage")

    @staticmethod
    def _get_images_metadata() -> ImagesMetadata:
        return ImagesMetadata.from_mapping(
            {
                _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
                _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
                _BASES_KEY: {
                    "ubuntu": {
                        _FROM_IMAGE_KEY: "ubuntu:latest",
                        _BASE_IMAGE_DISTRO_KEY: "Ubuntu",
                        _BASE_IMAGE_DESCRIPTION_KEY: "Default",
                        _OS_INSTALLER_KEY: "distro/debian/install.sh",
                        _TEST_SUITE_KEY: "default",
                    }
                },
                _AGENT_KEY: {
                    "codex": {
                        AGENT_PATH_KEY: "~/.codex",
                        AGENT_FULL_NAME_KEY: "Codex CLI",
                        AGENT_HOMEPAGE_KEY: "https://example.com",
                        BUILD_LOCAL_KEY: False,
                        _VALID_BASES_KEY: {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                    }
                },
            }
        )


def _build_config_context() -> ConfigContext:
    store = config_store_module.SettingsStore()
    project_path = Path.cwd().resolve()
    global_cfg = store.load_global()
    images_metadata = images_loader_module.load_images_metadata(global_cfg.local_image_repository)
    project_cfg = store.load_project(project_path)
    extensions = extensions_module.load_extensions()
    return ConfigContext(
        store=store,
        project_cfg=project_cfg,
        global_cfg=global_cfg,
        images_metadata=images_metadata,
        extensions=extensions,
    )
