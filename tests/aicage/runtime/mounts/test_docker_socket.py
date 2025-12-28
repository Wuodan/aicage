from pathlib import Path
from unittest import TestCase, mock

from aicage.config.project_config import AgentConfig, AgentMounts
from aicage.runtime.mounts._docker_socket import _resolve_docker_socket_mount


class DockerSocketMountTests(TestCase):
    def test_resolve_docker_socket_mount_persists_socket(self) -> None:
        agent_cfg = AgentConfig()
        with mock.patch("aicage.runtime.mounts._docker_socket.prompt_yes_no", return_value=True):
            mounts = _resolve_docker_socket_mount(agent_cfg, True)

        self.assertTrue(agent_cfg.mounts.docker)
        self.assertEqual(1, len(mounts))
        self.assertEqual(Path("/run/docker.sock"), mounts[0].container_path)

    def test_resolve_docker_socket_mount_uses_persisted_socket(self) -> None:
        agent_cfg = AgentConfig(mounts=AgentMounts(docker=True))
        with mock.patch("aicage.runtime.mounts._docker_socket.prompt_yes_no") as prompt_mock:
            mounts = _resolve_docker_socket_mount(agent_cfg, False)

        prompt_mock.assert_not_called()
        self.assertEqual(1, len(mounts))

    def test_resolve_docker_socket_mount_disabled(self) -> None:
        agent_cfg = AgentConfig()
        mounts = _resolve_docker_socket_mount(agent_cfg, False)

        self.assertEqual([], mounts)
