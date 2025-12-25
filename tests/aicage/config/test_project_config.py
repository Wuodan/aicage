from pathlib import Path
from unittest import TestCase

from aicage.config.project_config import ProjectConfig, ToolConfig


class ProjectConfigTests(TestCase):
    def test_from_mapping_applies_legacy_docker_args(self) -> None:
        data = {"tools": {"codex": {}}, "docker_args": "--net=host"}
        cfg = ProjectConfig.from_mapping(Path("/repo"), data)
        self.assertEqual("--net=host", cfg.tools["codex"].docker_args)

    def test_round_trip_mapping(self) -> None:
        cfg = ProjectConfig(path="/repo", tools={"codex": ToolConfig(base="ubuntu")})
        self.assertEqual({"path": "/repo", "tools": {"codex": {"base": "ubuntu"}}}, cfg.to_mapping())
