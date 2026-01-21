from unittest import TestCase, mock

from aicage.config.project_config import AgentConfig, _AgentMounts
from aicage.paths import CONTAINER_DOCKER_SOCKET_PATH
from aicage.runtime.docker_args._docker_socket import resolve_docker_socket_mount
from aicage.runtime.env_vars import DOCKER_HOST, WINDOWS_DOCKER_HOST


class DockerSocketMountTests(TestCase):
    def test_resolve_docker_socket_mount_persists_socket(self) -> None:
        agent_cfg = AgentConfig()
        with (
            mock.patch("aicage.runtime.docker_args._docker_socket.os.name", "posix"),
            mock.patch("aicage.runtime.docker_args._docker_socket.prompt_persist_docker_socket", return_value=True),
        ):
            mounts, env = resolve_docker_socket_mount(agent_cfg, True)

        self.assertTrue(agent_cfg.mounts.docker)
        self.assertEqual(1, len(mounts))
        self.assertEqual(CONTAINER_DOCKER_SOCKET_PATH, mounts[0].container_path)
        self.assertEqual([], env)

    def test_resolve_docker_socket_mount_uses_persisted_socket(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(docker=True))
        with (
            mock.patch("aicage.runtime.docker_args._docker_socket.os.name", "posix"),
            mock.patch("aicage.runtime.docker_args._docker_socket.prompt_persist_docker_socket") as prompt_mock,
        ):
            mounts, env = resolve_docker_socket_mount(agent_cfg, False)

        prompt_mock.assert_not_called()
        self.assertEqual(1, len(mounts))
        self.assertEqual([], env)

    def test_resolve_docker_socket_mount_disabled(self) -> None:
        agent_cfg = AgentConfig()
        mounts, env = resolve_docker_socket_mount(agent_cfg, False)

        self.assertEqual([], mounts)
        self.assertEqual([], env)

    def test_resolve_docker_socket_mount_windows_env(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(docker=True))
        with mock.patch("aicage.runtime.docker_args._docker_socket.os.name", "nt"):
            mounts, env = resolve_docker_socket_mount(agent_cfg, False)

        self.assertEqual([], mounts)
        self.assertEqual([(DOCKER_HOST, WINDOWS_DOCKER_HOST)], [(item.name, item.value) for item in env])
