from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

import yaml

from .errors import ConfigError
from .global_config import GlobalConfig
from .project_config import ProjectConfig
from .resources import find_packaged_path

_CONFIG_FILENAME = "config.yaml"
_DEFAULT_BASE_DIR = "~/.aicage"
_PROJECTS_SUBDIR = "projects"


class SettingsStore:
    """
    Persists per-project configuration under ~/.aicage.
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path(os.path.expanduser(_DEFAULT_BASE_DIR))
        self.projects_dir = self.base_dir / _PROJECTS_SUBDIR
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle)
                return data or {}
        except yaml.YAMLError as exc:
            raise ConfigError(f"Failed to parse YAML config at {path}: {exc}") from exc

    @staticmethod
    def _save_yaml(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle, sort_keys=True)

    def load_global(self) -> GlobalConfig:
        data = self._load_yaml(self._global_config())
        return GlobalConfig.from_mapping(data)

    def _project_path(self, project_realpath: Path) -> Path:
        digest = hashlib.sha256(str(project_realpath).encode("utf-8")).hexdigest()
        return self.projects_dir / f"{digest}.yaml"

    def load_project(self, project_realpath: Path) -> ProjectConfig:
        data = self._load_yaml(self._project_path(project_realpath))
        return ProjectConfig.from_mapping(project_realpath, data)

    def save_project(self, project_realpath: Path, config: ProjectConfig) -> None:
        self._save_yaml(self._project_path(project_realpath), config.to_mapping())


    @staticmethod
    def _global_config() -> Path:
        """
        Returns the path to the packaged global config file.
        """
        return find_packaged_path(_CONFIG_FILENAME)

    def project_config_path(self, project_realpath: Path) -> Path:
        """
        Returns the path to a project's config file under the base directory.
        """
        return self._project_path(project_realpath)
