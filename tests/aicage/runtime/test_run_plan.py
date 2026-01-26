from pathlib import Path
from unittest import TestCase, mock

from aicage.cli_types import ParsedArgs
from aicage.config.agent.models import AgentMetadata
from aicage.config.base.models import BaseMetadata
from aicage.config.context import ConfigContext
from aicage.config.project_config import ProjectConfig
from aicage.config.runtime_config import RunConfig
from aicage.registry.image_selection.models import ImageSelection
from aicage.runtime._agent_config import AgentConfig
from aicage.runtime.run_plan import build_run_args


class RunPlanTests(TestCase):
    def test_build_run_args_merges_docker_args(self) -> None:
        project_path = Path("/tmp/project")
        config = RunConfig(
            project_path=project_path,
            agent="codex",
            context=ConfigContext(
                store=mock.Mock(),
                project_cfg=ProjectConfig(path=str(project_path), agents={}),
                agents=self._get_agents(),
                bases=self._get_bases(),
                extensions={},
            ),
            selection=ImageSelection(
                image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                base="ubuntu",
                extensions=[],
                base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
            ),
            project_docker_args="--project",
            mounts=[],
            env=[],
        )
        parsed = ParsedArgs(False, "--cli", "codex", ["--flag"], False, None)
        agent_config = AgentConfig(agent_path=["~/.codex"], agent_config_host=[Path("/tmp/.codex")])

        with mock.patch("aicage.runtime.run_plan.resolve_agent_config", return_value=agent_config):
            run_args = build_run_args(config, parsed)

        self.assertEqual("--project --cli", run_args.merged_docker_args)
        self.assertEqual(["--flag"], run_args.agent_args)

    def test_build_run_args_uses_mounts_from_config(self) -> None:
        project_path = Path("/tmp/project")
        mount = mock.Mock()
        config = RunConfig(
            project_path=project_path,
            agent="codex",
            context=ConfigContext(
                store=mock.Mock(),
                project_cfg=ProjectConfig(path=str(project_path), agents={}),
                agents=self._get_agents(),
                bases=self._get_bases(),
                extensions={},
            ),
            selection=ImageSelection(
                image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                base="ubuntu",
                extensions=[],
                base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
            ),
            project_docker_args="",
            mounts=[mount],
            env=[],
        )
        parsed = ParsedArgs(False, "", "codex", [], False, None)
        agent_config = AgentConfig(agent_path=["~/.codex"], agent_config_host=[Path("/tmp/.codex")])

        with mock.patch("aicage.runtime.run_plan.resolve_agent_config", return_value=agent_config):
            run_args = build_run_args(config, parsed)

        self.assertEqual([mount], run_args.mounts)

    @staticmethod
    def _get_bases() -> dict[str, BaseMetadata]:
        return {
            "ubuntu": BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro="Ubuntu",
                base_image_description="Default",
                build_local=False,
                local_definition_dir=Path("/tmp/base"),
            )
        }

    @staticmethod
    def _get_agents() -> dict[str, AgentMetadata]:
        return {
            "codex": AgentMetadata(
                agent_path=["~/.codex"],
                agent_full_name="Codex CLI",
                agent_homepage="https://example.com",
                build_local=False,
                valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                local_definition_dir=Path("/tmp/agent"),
            )
        }
