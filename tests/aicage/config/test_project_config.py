from pathlib import Path
from unittest import TestCase

from aicage.config.project_config import AgentConfig, ProjectConfig


class ProjectConfigTests(TestCase):
    def test_from_mapping_applies_legacy_docker_args(self) -> None:
        data = {"agents": {"codex": {}}, "docker_args": "--net=host"}
        cfg = ProjectConfig.from_mapping(Path("/repo"), data)
        self.assertEqual("--net=host", cfg.agents["codex"].docker_args)

    def test_round_trip_mapping(self) -> None:
        cfg = ProjectConfig(path="/repo", agents={"codex": AgentConfig(base="ubuntu")})
        self.assertEqual({"path": "/repo", "agents": {"codex": {"base": "ubuntu"}}}, cfg.to_mapping())
