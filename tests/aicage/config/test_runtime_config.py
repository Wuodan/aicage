import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.cli_types import ParsedArgs
from aicage.config import SettingsStore
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
from aicage.config.project_config import AgentConfig, _AgentMounts
from aicage.config.runtime_config import RunConfig, load_run_config
from aicage.registry.image_selection import ImageSelection
from aicage.runtime.run_args import MountSpec


class RuntimeConfigTests(TestCase):
    def test_load_run_config_reads_docker_args_and_mount_prefs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            projects_dir = Path(tmp_dir)
            project_path = projects_dir / "project"
            project_path.mkdir()

            store = SettingsStore()

            project_cfg = store.load_project(project_path)
            project_cfg.agents["codex"] = AgentConfig(
                base="ubuntu",
                docker_args="--project",
                        mounts=_AgentMounts(gitconfig=True),
            )
            store.save_project(project_path, project_cfg)

            def store_factory(*args: object, **kwargs: object) -> SettingsStore:
                return SettingsStore()

            mounts = [MountSpec(host_path=Path("/tmp/host"), container_path=Path("/tmp/container"))]
            with (
                mock.patch("aicage.config.runtime_config.SettingsStore", new=store_factory),
                mock.patch("aicage.config.runtime_config.Path.cwd", return_value=project_path),
                mock.patch("aicage.config.runtime_config.resolve_mounts", return_value=mounts),
                mock.patch("aicage.config.runtime_config.load_extensions", return_value={}),
                mock.patch(
                    "aicage.config.runtime_config.load_images_metadata",
                    return_value=self._get_images_metadata(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.select_agent_image",
                    return_value=ImageSelection(
                        image_ref="ref",
                        base="ubuntu",
                        extensions=[],
                        base_image_ref="ref",
                    ),
                ),
            ):
                run_config = load_run_config("codex")

        self.assertIsInstance(run_config, RunConfig)
        self.assertEqual("--project", run_config.project_docker_args)
        self.assertEqual(mounts, run_config.mounts)

    def test_load_run_config_persists_new_docker_args(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()

            store = SettingsStore()
            project_cfg = store.load_project(project_path)
            project_cfg.agents["codex"] = AgentConfig(
                base="ubuntu",
                docker_args="--existing",
            )
            store.save_project(project_path, project_cfg)

            def store_factory(*args: object, **kwargs: object) -> SettingsStore:
                return SettingsStore()

            parsed = ParsedArgs(
                dry_run=False,
                docker_args="--new",
                agent="codex",
                agent_args=[],
                entrypoint=None,
                docker_socket=False,
                config_action=None,
            )
            with (
                mock.patch("aicage.config.runtime_config.SettingsStore", new=store_factory),
                mock.patch("aicage.config.runtime_config.Path.cwd", return_value=project_path),
                mock.patch("aicage.config.runtime_config.resolve_mounts", return_value=[]),
                mock.patch("aicage.config.runtime_config.load_extensions", return_value={}),
                mock.patch(
                    "aicage.config.runtime_config.load_images_metadata",
                    return_value=self._get_images_metadata(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.select_agent_image",
                    return_value=ImageSelection(
                        image_ref="ref",
                        base="ubuntu",
                        extensions=[],
                        base_image_ref="ref",
                    ),
                ),
                mock.patch("aicage.config.runtime_config.prompt_persist_docker_args", return_value=True),
            ):
                run_config = load_run_config("codex", parsed)

        self.assertEqual("--existing", run_config.project_docker_args)

    def test_load_run_config_defaults_base_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()

            store = SettingsStore()
            project_cfg = store.load_project(project_path)
            project_cfg.agents["codex"] = AgentConfig()
            store.save_project(project_path, project_cfg)

            def store_factory(*args: object, **kwargs: object) -> SettingsStore:
                return SettingsStore()

            with (
                mock.patch("aicage.config.runtime_config.SettingsStore", new=store_factory),
                mock.patch("aicage.config.runtime_config.Path.cwd", return_value=project_path),
                mock.patch("aicage.config.runtime_config.resolve_mounts", return_value=[]),
                mock.patch("aicage.config.runtime_config.load_extensions", return_value={}),
                mock.patch(
                    "aicage.config.runtime_config.load_images_metadata",
                    return_value=self._get_images_metadata(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.select_agent_image",
                    return_value=ImageSelection(
                        image_ref="ref",
                        base="ubuntu",
                        extensions=[],
                        base_image_ref="ref",
                    ),
                ),
            ):
                run_config = load_run_config("codex")

        self.assertEqual("ubuntu", run_config.selection.base)

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
