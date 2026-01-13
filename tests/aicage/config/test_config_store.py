import hashlib
import tempfile
from pathlib import Path
from unittest import TestCase, mock

import yaml

from aicage.config import ProjectConfig, SettingsStore
from aicage.config.project_config import AgentConfig, _AgentMounts


class ConfigStoreTests(TestCase):
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
