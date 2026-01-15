import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.cli_types import ParsedArgs
from aicage.config.config_store import SettingsStore
from aicage.config.images_metadata.models import (
    AgentMetadata,
    BaseMetadata,
    ImagesMetadata,
)
from aicage.config.project_config import AgentConfig, _AgentMounts
from aicage.config.runtime_config import RunConfig, load_run_config
from aicage.registry.image_selection.models import ImageSelection
from aicage.runtime.run_args import MountSpec


class RuntimeConfigTests(TestCase):
    def test_load_run_config_reads_docker_args_and_mount_prefs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            projects_dir = Path(tmp_dir)
            project_path = projects_dir / "project"
            project_path.mkdir()

            store = SettingsStore()

            project_cfg = store.load_project(project_path)
            project_cfg.agents["codex"] = AgentConfig(
                base="ubuntu",
                docker_args="--project",
                        mounts=_AgentMounts(gitconfig=True),
            )
            store.save_project(project_path, project_cfg)

            def store_factory(*args: object, **kwargs: object) -> SettingsStore:
                return SettingsStore()

            mounts = [MountSpec(host_path=Path("/tmp/host"), container_path=Path("/tmp/container"))]
            with (
                mock.patch("aicage.config.runtime_config.SettingsStore", new=store_factory),
                mock.patch("aicage.config.runtime_config.Path.cwd", return_value=project_path),
                mock.patch("aicage.config.runtime_config.resolve_mounts", return_value=mounts),
                mock.patch("aicage.config.runtime_config.load_extensions", return_value={}),
                mock.patch(
                    "aicage.config.runtime_config.load_bases",
                    return_value=self._get_bases(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_agents",
                    return_value=self._get_agents(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_images_metadata",
                    return_value=self._get_images_metadata(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.select_agent_image",
                    return_value=ImageSelection(
                        image_ref="ref",
                        base="ubuntu",
                        extensions=[],
                        base_image_ref="ref",
                    ),
                ),
            ):
                run_config = load_run_config("codex")

        self.assertIsInstance(run_config, RunConfig)
        self.assertEqual("--project", run_config.project_docker_args)
        self.assertEqual(mounts, run_config.mounts)

    def test_load_run_config_persists_new_docker_args(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()

            store = SettingsStore()
            project_cfg = store.load_project(project_path)
            project_cfg.agents["codex"] = AgentConfig(
                base="ubuntu",
                docker_args="--existing",
            )
            store.save_project(project_path, project_cfg)

            def store_factory(*args: object, **kwargs: object) -> SettingsStore:
                return SettingsStore()

            parsed = ParsedArgs(
                dry_run=False,
                docker_args="--new",
                agent="codex",
                agent_args=[],
                entrypoint=None,
                docker_socket=False,
                config_action=None,
            )
            with (
                mock.patch("aicage.config.runtime_config.SettingsStore", new=store_factory),
                mock.patch("aicage.config.runtime_config.Path.cwd", return_value=project_path),
                mock.patch("aicage.config.runtime_config.resolve_mounts", return_value=[]),
                mock.patch("aicage.config.runtime_config.load_extensions", return_value={}),
                mock.patch(
                    "aicage.config.runtime_config.load_bases",
                    return_value=self._get_bases(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_agents",
                    return_value=self._get_agents(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_images_metadata",
                    return_value=self._get_images_metadata(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.select_agent_image",
                    return_value=ImageSelection(
                        image_ref="ref",
                        base="ubuntu",
                        extensions=[],
                        base_image_ref="ref",
                    ),
                ),
                mock.patch("aicage.config.runtime_config.prompt_persist_docker_args", return_value=True),
            ):
                run_config = load_run_config("codex", parsed)

        self.assertEqual("--existing", run_config.project_docker_args)

    def test_load_run_config_defaults_base_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()

            store = SettingsStore()
            project_cfg = store.load_project(project_path)
            project_cfg.agents["codex"] = AgentConfig()
            store.save_project(project_path, project_cfg)

            def store_factory(*args: object, **kwargs: object) -> SettingsStore:
                return SettingsStore()

            with (
                mock.patch("aicage.config.runtime_config.SettingsStore", new=store_factory),
                mock.patch("aicage.config.runtime_config.Path.cwd", return_value=project_path),
                mock.patch("aicage.config.runtime_config.resolve_mounts", return_value=[]),
                mock.patch("aicage.config.runtime_config.load_extensions", return_value={}),
                mock.patch(
                    "aicage.config.runtime_config.load_bases",
                    return_value=self._get_bases(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_agents",
                    return_value=self._get_agents(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_images_metadata",
                    return_value=self._get_images_metadata(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.select_agent_image",
                    return_value=ImageSelection(
                        image_ref="ref",
                        base="ubuntu",
                        extensions=[],
                        base_image_ref="ref",
                    ),
                ),
            ):
                run_config = load_run_config("codex")

        self.assertEqual("ubuntu", run_config.selection.base)

    @staticmethod
    def _get_images_metadata() -> ImagesMetadata:
        return ImagesMetadata(
            bases=RuntimeConfigTests._get_bases(),
            agents=RuntimeConfigTests._get_agents(),
        )

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
