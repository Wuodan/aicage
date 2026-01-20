from pathlib import Path, PurePosixPath
from unittest import TestCase, mock

from aicage.cli_types import ParsedArgs
from aicage.config.agent.models import AgentMetadata
from aicage.config.base.models import BaseMetadata
from aicage.config.context import ConfigContext
from aicage.config.project_config import AgentConfig, ProjectConfig
from aicage.runtime.mounts import resolver
from aicage.runtime.run_args import MountSpec


class ResolverTests(TestCase):
    def test_resolve_mounts_aggregates_mounts(self) -> None:
        project_cfg = ProjectConfig(path="/tmp/project", agents={"codex": AgentConfig()})
        context = ConfigContext(
            store=mock.Mock(),
            project_cfg=project_cfg,
            agents=self._get_agents(),
            bases=self._get_bases(),
            extensions={},
        )
        parsed = ParsedArgs(False, "", "codex", [], None, False, None)
        git_mount = MountSpec(host_path=Path("/tmp/git"), container_path=PurePosixPath("/git"))
        ssh_mount = MountSpec(host_path=Path("/tmp/ssh"), container_path=PurePosixPath("/ssh"))
        gpg_mount = MountSpec(host_path=Path("/tmp/gpg"), container_path=PurePosixPath("/gpg"))
        entry_mount = MountSpec(
            host_path=Path("/tmp/entry"),
            container_path=PurePosixPath("/entry"),
            read_only=True,
        )
        docker_mount = MountSpec(
            host_path=Path("/tmp/docker"),
            container_path=PurePosixPath("/run/docker.sock"),
        )

        with (
            mock.patch("aicage.runtime.mounts.resolver.resolve_git_config_mount", return_value=[git_mount]) as git_mock,
            mock.patch("aicage.runtime.mounts.resolver.resolve_ssh_mount", return_value=[ssh_mount]) as ssh_mock,
            mock.patch("aicage.runtime.mounts.resolver.resolve_gpg_mount", return_value=[gpg_mount]) as gpg_mock,
            mock.patch(
                "aicage.runtime.mounts.resolver.resolve_entrypoint_mount", return_value=[entry_mount]
            ) as entry_mock,
            mock.patch(
                "aicage.runtime.mounts.resolver.resolve_docker_socket_mount", return_value=[docker_mount]
            ) as docker_mock,
        ):
            mounts = resolver.resolve_mounts(context, "codex", parsed)

        self.assertEqual([git_mount, ssh_mount, gpg_mount, entry_mount, docker_mount], mounts)
        git_mock.assert_called_once_with(project_cfg.agents["codex"])
        ssh_mock.assert_called_once_with(Path("/tmp/project"), project_cfg.agents["codex"])
        gpg_mock.assert_called_once_with(Path("/tmp/project"), project_cfg.agents["codex"])
        entry_mock.assert_called_once_with(project_cfg.agents["codex"], None)
        docker_mock.assert_called_once_with(project_cfg.agents["codex"], False)

    def test_resolve_mounts_inserts_agent_config(self) -> None:
        project_cfg = ProjectConfig(path="/tmp/project", agents={})
        context = ConfigContext(
            store=mock.Mock(),
            project_cfg=project_cfg,
            agents=self._get_agents(),
            bases=self._get_bases(),
            extensions={},
        )

        with (
            mock.patch("aicage.runtime.mounts.resolver.resolve_git_config_mount", return_value=[]),
            mock.patch("aicage.runtime.mounts.resolver.resolve_ssh_mount", return_value=[]),
            mock.patch("aicage.runtime.mounts.resolver.resolve_gpg_mount", return_value=[]),
            mock.patch("aicage.runtime.mounts.resolver.resolve_entrypoint_mount", return_value=[]),
            mock.patch("aicage.runtime.mounts.resolver.resolve_docker_socket_mount", return_value=[]),
        ):
            resolver.resolve_mounts(context, "codex", None)

        self.assertIsInstance(project_cfg.agents["codex"], AgentConfig)

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
                agent_path="~/.codex",
                agent_full_name="Codex CLI",
                agent_homepage="https://example.com",
                build_local=False,
                valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                local_definition_dir=Path("/tmp/agent"),
            )
        }
