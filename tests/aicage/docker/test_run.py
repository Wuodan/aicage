import os
from pathlib import Path
from unittest import TestCase, mock

from docker.errors import ContainerError, DockerException
from docker.models.containers import Container

from aicage.docker import run
from aicage.runtime.run_args import DockerRunArgs, MountSpec


class RunCommandTests(TestCase):
    def test_run_builder_version_check_returns_output(self) -> None:
        client = mock.Mock()
        client.containers.run.return_value = b"1.2.3\n"
        with mock.patch("aicage.docker.run.get_docker_client", return_value=client):
            result = run.run_builder_version_check(
                "ghcr.io/aicage/aicage-image-util:agent-version",
                Path("/tmp/agent"),
            )
        self.assertEqual(0, result.returncode)
        self.assertEqual("1.2.3\n", result.stdout)
        self.assertEqual("", result.stderr)

    def test_run_builder_version_check_handles_container_error(self) -> None:
        error = ContainerError(
            container=mock.Mock(spec=Container),
            exit_status=2,
            command=["/bin/bash", "/agent/version.sh"],
            image="ghcr.io/aicage/aicage-image-util:agent-version",
            stderr="failed",
        )
        error.stdout = b"partial"
        client = mock.Mock()
        client.containers.run.side_effect = error
        with mock.patch("aicage.docker.run.get_docker_client", return_value=client):
            result = run.run_builder_version_check(
                "ghcr.io/aicage/aicage-image-util:agent-version",
                Path("/tmp/agent"),
            )
        self.assertEqual(2, result.returncode)
        self.assertEqual("partial", result.stdout)
        self.assertEqual("failed", result.stderr)

    def test_run_builder_version_check_handles_docker_error(self) -> None:
        client = mock.Mock()
        client.containers.run.side_effect = DockerException("boom")
        with mock.patch("aicage.docker.run.get_docker_client", return_value=client):
            result = run.run_builder_version_check(
                "ghcr.io/aicage/aicage-image-util:agent-version",
                Path("/tmp/agent"),
            )
        self.assertEqual(1, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertEqual("boom", result.stderr)

    def test_resolve_user_ids_handles_missing(self) -> None:
        with mock.patch("aicage.docker.run.os.getuid", side_effect=AttributeError), mock.patch(
            "aicage.docker.run.os.getgid", side_effect=AttributeError
        ), mock.patch.dict(os.environ, {"USER": "tester"}, clear=True):
            env_flags = run._resolve_user_ids()
        self.assertEqual(["-e", "AICAGE_USER=tester"], env_flags)

    def test_resolve_user_ids_includes_uid_gid(self) -> None:
        with mock.patch("aicage.docker.run.os.getuid", return_value=1000), mock.patch(
            "aicage.docker.run.os.getgid", return_value=1001
        ), mock.patch.dict(os.environ, {"USER": "tester"}, clear=True):
            env_flags = run._resolve_user_ids()
        self.assertEqual(
            ["-e", "AICAGE_UID=1000", "-e", "AICAGE_GID=1001", "-e", "AICAGE_USER=tester"],
            env_flags,
        )

    def test_assemble_includes_workspace_mount(self) -> None:
        with mock.patch("aicage.docker.run._resolve_user_ids", return_value=[]):
            run_args = DockerRunArgs(
                image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                project_path=Path("/work/project"),
                agent_config_host=Path("/host/.codex"),
                agent_config_mount_container=Path("/aicage/agent-config"),
                merged_docker_args="--network=host",
                agent_args=["--flag"],
                agent_path="~/.codex",
            )
            cmd = run._assemble_docker_run(run_args)
        self.assertEqual(
            [
                "docker",
                "run",
                "--rm",
                "-it",
                "-e",
                "AICAGE_WORKSPACE=/work/project",
                "-e",
                "AICAGE_AGENT_CONFIG_PATH=~/.codex",
                "-v",
                "/work/project:/workspace",
                "-v",
                "/work/project:/work/project",
                "-v",
                "/host/.codex:/aicage/agent-config",
                "--network=host",
                "ghcr.io/aicage/aicage:codex-ubuntu",
                "--flag",
            ],
            cmd,
        )

    def test_assemble_includes_env_and_mounts(self) -> None:
        with mock.patch("aicage.docker.run._resolve_user_ids", return_value=["-e", "AICAGE_USER=me"]):
            run_args = DockerRunArgs(
                image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                project_path=Path("/work/project"),
                agent_config_host=Path("/host/.codex"),
                agent_config_mount_container=Path("/aicage/agent-config"),
                merged_docker_args="--net=host",
                agent_args=["--flag"],
                agent_path=None,
                env=["EXTRA=1"],
                mounts=[MountSpec(host_path=Path("/tmp/one"), container_path=Path("/opt/one"), read_only=True)],
            )
            cmd = run._assemble_docker_run(run_args)
        self.assertIn("-e", cmd)
        self.assertIn("EXTRA=1", cmd)
        self.assertIn("-v", cmd)
        self.assertIn("/tmp/one:/opt/one:ro", cmd)
        self.assertNotIn("AICAGE_AGENT_CONFIG_PATH", " ".join(cmd))
