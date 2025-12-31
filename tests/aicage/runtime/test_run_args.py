import os
from pathlib import Path
from unittest import TestCase, mock

from aicage.runtime import run_args
from aicage.runtime.run_args import DockerRunArgs, MountSpec, assemble_docker_run, merge_docker_args


class RunArgsTests(TestCase):
    def test_merge_docker_args(self) -> None:
        merged = merge_docker_args("--one", "", "--two")
        self.assertEqual("--one --two", merged)

    def test_resolve_user_ids_handles_missing(self) -> None:
        with mock.patch("aicage.runtime.run_args.os.getuid", side_effect=AttributeError), mock.patch(
            "aicage.runtime.run_args.os.getgid", side_effect=AttributeError
        ), mock.patch.dict(os.environ, {"USER": "tester"}, clear=True):
            env_flags = run_args._resolve_user_ids()  # noqa: SLF001
        self.assertEqual(["-e", "AICAGE_USER=tester"], env_flags)

    def test_resolve_user_ids_includes_uid_gid(self) -> None:
        with mock.patch("aicage.runtime.run_args.os.getuid", return_value=1000), mock.patch(
            "aicage.runtime.run_args.os.getgid", return_value=1001
        ), mock.patch.dict(os.environ, {"USER": "tester"}, clear=True):
            env_flags = run_args._resolve_user_ids()  # noqa: SLF001
        self.assertEqual(
            ["-e", "AICAGE_UID=1000", "-e", "AICAGE_GID=1001", "-e", "AICAGE_USER=tester"],
            env_flags,
        )

    def test_assemble_includes_workspace_mount(self) -> None:
        with mock.patch("aicage.runtime.run_args._resolve_user_ids", return_value=[]):
            run_args = DockerRunArgs(
                image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                project_path=Path("/work/project"),
                agent_config_host=Path("/host/.codex"),
                agent_config_mount_container=Path("/aicage/agent-config"),
                merged_docker_args="--network=host",
                agent_args=["--flag"],
                agent_path="~/.codex",
            )
            cmd = assemble_docker_run(run_args)
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
        with mock.patch("aicage.runtime.run_args._resolve_user_ids", return_value=["-e", "AICAGE_USER=me"]):
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
            cmd = assemble_docker_run(run_args)
        self.assertIn("-e", cmd)
        self.assertIn("EXTRA=1", cmd)
        self.assertIn("-v", cmd)
        self.assertIn("/tmp/one:/opt/one:ro", cmd)
        self.assertNotIn("AICAGE_AGENT_CONFIG_PATH", " ".join(cmd))
