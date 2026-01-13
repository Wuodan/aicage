import hashlib
import tempfile
from pathlib import Path
from unittest import TestCase, mock

import yaml

from aicage.config import ProjectConfig, SettingsStore
from aicage.config.global_config import (
    _DEFAULT_IMAGE_BASE_KEY,
    _IMAGE_BASE_REPOSITORY_KEY,
    _IMAGE_REGISTRY_API_TOKEN_URL_KEY,
    _IMAGE_REGISTRY_API_URL_KEY,
    _IMAGE_REGISTRY_KEY,
    _IMAGE_REPOSITORY_KEY,
    _LOCAL_IMAGE_REPOSITORY_KEY,
    _VERSION_CHECK_IMAGE_KEY,
)
from aicage.config.project_config import AgentConfig, _AgentMounts
from aicage.paths import CONFIG_FILENAME


class ConfigStoreTests(TestCase):
    def test_load_global_reads_packaged_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            packaged_dir = base_dir / "packaged"
            packaged_dir.mkdir(parents=True, exist_ok=True)
            packaged_config = packaged_dir / CONFIG_FILENAME
            packaged_config.write_text(
                yaml.safe_dump(
                    {
                        _IMAGE_REGISTRY_KEY: "ghcr.io",
                        _IMAGE_REGISTRY_API_URL_KEY: "https://ghcr.io/v2",
                        _IMAGE_REGISTRY_API_TOKEN_URL_KEY: "https://ghcr.io/token",
                        _IMAGE_REPOSITORY_KEY: "aicage/aicage",
                        _IMAGE_BASE_REPOSITORY_KEY: "aicage/aicage-image-base",
                        _DEFAULT_IMAGE_BASE_KEY: "ubuntu",
                        _VERSION_CHECK_IMAGE_KEY: "ghcr.io/aicage/aicage-image-util:agent-version",
                    _LOCAL_IMAGE_REPOSITORY_KEY: "aicage",
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )

            with mock.patch(
                    "aicage.config.config_store.find_packaged_path",
                    return_value=packaged_config,
                ):
                store = SettingsStore()
                global_cfg = store.load_global()
                self.assertEqual("aicage/aicage", global_cfg.image_repository)
                self.assertEqual("ubuntu", global_cfg.default_image_base)
                self.assertEqual({}, global_cfg.agents)

    def test_project_config_path_returns_hashed_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            projects_dir = Path(tmp_dir)

            with mock.patch(
                    "aicage.config.config_store.PROJECTS_DIR",
                    projects_dir,
                ):
                store = SettingsStore()
                project_path = Path("/repo")
                expected = hashlib.sha256(str(project_path).encode("utf-8")).hexdigest()

                path = store.project_config_path(project_path)

            self.assertEqual(store.projects_dir / f"{expected}.yaml", path)

    def test_load_project_returns_empty_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            projects_dir = Path(tmp_dir)

            with mock.patch(
                    "aicage.config.config_store.PROJECTS_DIR",
                    projects_dir,
                ):
                store = SettingsStore()
                project_path = projects_dir / "project"
                project_path.mkdir(parents=True, exist_ok=True)

                project_cfg = store.load_project(project_path)

            self.assertEqual(ProjectConfig(path=str(project_path), agents={}), project_cfg)

    def test_save_project_writes_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            projects_dir = Path(tmp_dir)

            with mock.patch(
                    "aicage.config.config_store.PROJECTS_DIR",
                    projects_dir,
                ):
                store = SettingsStore()
                project_path = projects_dir / "project"
                project_path.mkdir(parents=True, exist_ok=True)

                project_cfg = ProjectConfig(path=str(project_path), agents={})
                project_cfg.agents["codex"] = AgentConfig(
                    base="fedora",
                    docker_args="--add-host=host.docker.internal:host-gateway",
                    mounts=_AgentMounts(),
                )
                store.save_project(project_path, project_cfg)

                config_path = store.project_config_path(project_path)
                with config_path.open("r", encoding="utf-8") as handle:
                    raw = yaml.safe_load(handle)

            self.assertEqual(project_cfg.to_mapping(), raw)
