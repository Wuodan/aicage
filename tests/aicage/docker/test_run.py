import os
from pathlib import Path, PurePosixPath
from unittest import TestCase, mock

from docker.errors import ContainerError, DockerException
from docker.models.containers import Container

from aicage.docker import run
from aicage.paths import CONTAINER_AGENT_CONFIG_DIR, CONTAINER_WORKSPACE_DIR, container_project_path
from aicage.runtime.run_args import DockerRunArgs, MountSpec


class RunCommandTests(TestCase):
    @staticmethod
    def test_run_container_executes_command() -> None:
        args = DockerRunArgs(
            image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
            project_path=Path("/work/project"),
            agent_config_host=Path("/host/.codex"),
            agent_config_mount_container=CONTAINER_AGENT_CONFIG_DIR,
            merged_docker_args="",
            agent_args=["--flag"],
            agent_path=None,
        )
        with (
            mock.patch("aicage.docker.run._assemble_docker_run", return_value=["docker", "run"]),
            mock.patch("aicage.docker.run.subprocess.run") as run_mock,
        ):
            run.run_container(args)

        run_mock.assert_called_once_with(["docker", "run"], check=True)

    @staticmethod
    def test_print_run_command_outputs_command() -> None:
        args = DockerRunArgs(
            image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
            project_path=Path("/work/project"),
            agent_config_host=Path("/host/.codex"),
            agent_config_mount_container=CONTAINER_AGENT_CONFIG_DIR,
            merged_docker_args="",
            agent_args=[],
            agent_path=None,
        )
        with (
            mock.patch("aicage.docker.run._assemble_docker_run", return_value=["docker", "run", "image"]),
            mock.patch("builtins.print") as print_mock,
        ):
            run.print_run_command(args)

        print_mock.assert_called_once_with("docker run image")

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
        with (
            mock.patch("aicage.docker.run.os.getuid", None, create=True),
            mock.patch("aicage.docker.run.os.getgid", None, create=True),
            mock.patch.dict(os.environ, {"USER": "tester"}, clear=True),
            mock.patch("aicage.docker.run.os.name", "posix"),
        ):
            env_flags = run._resolve_user_ids()
        self.assertEqual(["-e", "AICAGE_USER=tester"], env_flags)

    def test_resolve_user_ids_includes_uid_gid(self) -> None:
        with (
            mock.patch("aicage.docker.run.os.getuid", return_value=1000, create=True),
            mock.patch("aicage.docker.run.os.getgid", return_value=1001, create=True),
            mock.patch.dict(os.environ, {"USER": "tester"}, clear=True),
            mock.patch("aicage.docker.run.os.name", "posix"),
        ):
            env_flags = run._resolve_user_ids()
        self.assertEqual(
            ["-e", "AICAGE_UID=1000", "-e", "AICAGE_GID=1001", "-e", "AICAGE_USER=tester"],
            env_flags,
        )

    def test_resolve_user_ids_sets_root_on_windows(self) -> None:
        with mock.patch("aicage.docker.run.os.getuid", side_effect=AttributeError, create=True), mock.patch(
            "aicage.docker.run.os.getgid", side_effect=AttributeError, create=True
        ), mock.patch.dict(os.environ, {"USER": "tester"}, clear=True), mock.patch("aicage.docker.run.os.name", "nt"):
            env_flags = run._resolve_user_ids()
        self.assertEqual(["-e", "AICAGE_USER=root"], env_flags)

    def test_assemble_includes_workspace_mount(self) -> None:
        with (
            mock.patch("aicage.docker.run._resolve_user_ids", return_value=[]),
            mock.patch("aicage.paths.os.name", "posix"),
        ):
            run_args = DockerRunArgs(
                image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                project_path=Path("/work/project"),
                agent_config_host=Path("/host/.codex"),
                agent_config_mount_container=CONTAINER_AGENT_CONFIG_DIR,
                merged_docker_args="--network=host",
                agent_args=["--flag"],
                agent_path="~/.codex",
            )
            cmd = run._assemble_docker_run(run_args)
        host_project_path = str(run_args.project_path)
        container_project_path = PurePosixPath("/work/project").as_posix()
        agent_config_host = str(run_args.agent_config_host)
        self.assertEqual(
            [
                "docker",
                "run",
                "--rm",
                "-it",
                "-e",
                f"AICAGE_WORKSPACE={container_project_path}",
                "-e",
                "AICAGE_AGENT_CONFIG_PATH=~/.codex",
                "-v",
                f"{host_project_path}:{CONTAINER_WORKSPACE_DIR.as_posix()}",
                "-v",
                f"{host_project_path}:{container_project_path}",
                "-v",
                f"{agent_config_host}:{CONTAINER_AGENT_CONFIG_DIR.as_posix()}",
                "--network=host",
                "ghcr.io/aicage/aicage:codex-ubuntu",
                "--flag",
            ],
            cmd,
        )

    def test_assemble_windows_uses_container_workspace(self) -> None:
        project_path = Path("C:/work/project")
        agent_config_host = Path("C:/host/.codex")
        with (
            mock.patch("aicage.docker.run._resolve_user_ids", return_value=[]),
            mock.patch("aicage.paths.os.name", "nt"),
        ):
            run_args = DockerRunArgs(
                image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                project_path=project_path,
                agent_config_host=agent_config_host,
                agent_config_mount_container=CONTAINER_AGENT_CONFIG_DIR,
                merged_docker_args="",
                agent_args=[],
                agent_path=None,
            )
            cmd = run._assemble_docker_run(run_args)
            windows_workspace = container_project_path(project_path).as_posix()
        workspace_root = CONTAINER_WORKSPACE_DIR.as_posix()
        self.assertIn(f"AICAGE_WORKSPACE={windows_workspace}", cmd)
        self.assertIn(f"{project_path}:{workspace_root}", cmd)
        self.assertIn(f"{project_path}:{windows_workspace}", cmd)

    def test_assemble_includes_env_and_mounts(self) -> None:
        with mock.patch("aicage.docker.run._resolve_user_ids", return_value=["-e", "AICAGE_USER=me"]):
            run_args = DockerRunArgs(
                image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                project_path=Path("/work/project"),
                agent_config_host=Path("/host/.codex"),
                agent_config_mount_container=CONTAINER_AGENT_CONFIG_DIR,
                merged_docker_args="--net=host",
                agent_args=["--flag"],
                agent_path=None,
                env=["EXTRA=1"],
                mounts=[
                    MountSpec(
                        host_path=Path("/tmp/one"),
                        container_path=PurePosixPath("/opt/one"),
                        read_only=True,
                    )
                ],
            )
            cmd = run._assemble_docker_run(run_args)
        self.assertIn("-e", cmd)
        self.assertIn("EXTRA=1", cmd)
        self.assertIn("-v", cmd)
        self.assertIn(f"{Path('/tmp/one')}:{PurePosixPath('/opt/one').as_posix()}:ro", cmd)
        self.assertNotIn("AICAGE_AGENT_CONFIG_PATH", " ".join(cmd))
