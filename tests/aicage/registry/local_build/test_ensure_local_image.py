import tempfile
from pathlib import Path
from unittest import TestCase, mock

import yaml

from aicage.config.context import ConfigContext
from aicage.config.images_metadata.models import (
    AgentMetadata,
    ImagesMetadata,
    BaseMetadata,
    _ImageReleaseInfo,
)
from aicage.config.project_config import ProjectConfig
from aicage.config.runtime_config import RunConfig
from aicage.registry.errors import RegistryError
from aicage.registry.image_selection import ImageSelection
from aicage.registry.local_build import ensure_local_image as ensure_local_image_module
from aicage.registry.local_build._store import (
    _AGENT_KEY,
    _AGENT_VERSION_KEY,
    _BASE_IMAGE_KEY,
    _BASE_KEY,
    _BUILT_AT_KEY,
    _IMAGE_REF_KEY,
)

from ._fixtures import build_run_config


class EnsureLocalImageTests(TestCase):
    def test_ensure_local_image_raises_without_definition(self) -> None:
        run_config = build_run_config(build_local=True)
        agent_metadata = run_config.context.images_metadata.agents[run_config.agent]
        run_config.context.images_metadata.agents[run_config.agent] = AgentMetadata(
            agent_path=agent_metadata.agent_path,
            agent_full_name=agent_metadata.agent_full_name,
            agent_homepage=agent_metadata.agent_homepage,
            build_local=agent_metadata.build_local,
            valid_bases=agent_metadata.valid_bases,
            base_exclude=agent_metadata.base_exclude,
            base_distro_exclude=agent_metadata.base_distro_exclude,
            local_definition_dir=None,
        )
        with mock.patch(
            "aicage.registry.local_build.ensure_local_image.refresh_base_digest"
        ) as refresh_mock:
            with self.assertRaises(RegistryError):
                ensure_local_image_module.ensure_local_image(run_config)
        refresh_mock.assert_not_called()

    def test_ensure_local_image_runs_for_custom_agent(self) -> None:
        run_config = self._build_custom_run_config()
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_dir = Path(tmp_dir) / "state"
            with (
                mock.patch(
                    "aicage.registry.local_build._store.paths_module.IMAGE_BUILD_STATE_DIR",
                    state_dir,
                ),
                mock.patch(
                    "aicage.registry.local_build.ensure_local_image.refresh_base_digest",
                    return_value="sha256:base",
                ) as refresh_mock,
                mock.patch(
                    "aicage.registry.local_build.ensure_local_image.should_build",
                    return_value=False,
                ),
                mock.patch(
                    "aicage.registry.local_build.ensure_local_image.AgentVersionChecker"
                ) as checker_cls,
            ):
                checker_cls.return_value.get_version.return_value = "1.2.3"
                ensure_local_image_module.ensure_local_image(run_config)
            refresh_mock.assert_called_once()

    def test_ensure_local_image_raises_on_version_failure(self) -> None:
        run_config = build_run_config()
        with (
            mock.patch(
                "aicage.registry.local_build.ensure_local_image.refresh_base_digest",
                return_value="sha256:base",
            ),
            mock.patch(
                "aicage.registry.local_build.ensure_local_image.AgentVersionChecker"
            ) as checker_cls,
        ):
            checker_cls.return_value.get_version.side_effect = RegistryError("version failed")
            with self.assertRaises(RegistryError):
                ensure_local_image_module.ensure_local_image(run_config)

    @staticmethod
    def test_ensure_local_image_uses_custom_base() -> None:
        run_config = build_run_config()
        run_config = RunConfig(
            project_path=run_config.project_path,
            agent=run_config.agent,
            context=run_config.context,
            selection=ImageSelection(
                image_ref="aicage:claude-custom",
                base="custom",
                extensions=[],
                base_image_ref="aicage:claude-custom",
            ),
            project_docker_args=run_config.project_docker_args,
            mounts=run_config.mounts,
        )
        custom_base = BaseMetadata(
            from_image="ubuntu:latest",
            base_image_distro="Ubuntu",
            base_image_description="Custom",
        )
        run_config.context.custom_bases = {"custom": custom_base}
        with (
            mock.patch(
                "aicage.registry.local_build.ensure_local_image.ensure_custom_base_image"
            ) as base_mock,
            mock.patch(
                "aicage.registry.local_build.ensure_local_image.refresh_base_digest"
            ) as refresh_mock,
            mock.patch(
                "aicage.registry.local_build.ensure_local_image.should_build",
                return_value=False,
            ),
            mock.patch(
                "aicage.registry.local_build.ensure_local_image.AgentVersionChecker"
            ) as checker_cls,
        ):
            checker_cls.return_value.get_version.return_value = "1.2.3"
            ensure_local_image_module.ensure_local_image(run_config)
        base_mock.assert_called_once()
        refresh_mock.assert_not_called()

    def test_ensure_local_image_builds_when_missing_image(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_dir = Path(tmp_dir) / "state"
            log_dir = Path(tmp_dir) / "logs"
            run_config = build_run_config()

            with (
                mock.patch(
                    "aicage.registry.local_build._store.paths_module.IMAGE_BUILD_STATE_DIR",
                    state_dir,
                ),
                mock.patch(
                    "aicage.registry.local_build._logs.IMAGE_BUILD_LOG_DIR",
                    log_dir,
                ),
                mock.patch(
                    "aicage.registry.local_build._plan.local_image_exists",
                    return_value=False,
                ),
                mock.patch(
                    "aicage.registry.local_build.ensure_local_image.refresh_base_digest",
                    return_value="sha256:base",
                ),
                mock.patch(
                    "aicage.registry.local_build.ensure_local_image.run_build"
                ) as build_mock,
                mock.patch(
                    "aicage.registry.local_build.ensure_local_image.AgentVersionChecker"
                ) as checker_cls,
            ):
                checker_cls.return_value.get_version.return_value = "1.2.3"
                ensure_local_image_module.ensure_local_image(run_config)

            build_mock.assert_called_once()
            record_path = state_dir / "claude-ubuntu.yaml"
            payload = yaml.safe_load(record_path.read_text(encoding="utf-8"))
            self.assertEqual("1.2.3", payload[_AGENT_VERSION_KEY])

    @staticmethod
    def test_ensure_local_image_skips_when_up_to_date() -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_dir = Path(tmp_dir) / "state"
            log_dir = Path(tmp_dir) / "logs"
            run_config = build_run_config()
            record_path = state_dir / "claude-ubuntu.yaml"
            record_path.parent.mkdir(parents=True, exist_ok=True)
            record_path.write_text(
                yaml.safe_dump(
                    {
                        _AGENT_KEY: "claude",
                        _BASE_KEY: "ubuntu",
                        _AGENT_VERSION_KEY: "1.2.3",
                        _BASE_IMAGE_KEY: "ghcr.io/aicage/aicage-image-base:ubuntu",
                        _IMAGE_REF_KEY: "aicage:claude-ubuntu",
                        _BUILT_AT_KEY: "2024-01-01T00:00:00+00:00",
                    }
                ),
                encoding="utf-8",
            )

            with (
                mock.patch(
                    "aicage.registry.local_build._store.paths_module.IMAGE_BUILD_STATE_DIR",
                    state_dir,
                ),
                mock.patch(
                    "aicage.registry.local_build._logs.IMAGE_BUILD_LOG_DIR",
                    log_dir,
                ),
                mock.patch(
                    "aicage.registry.local_build._plan.local_image_exists",
                    return_value=True,
                ),
                mock.patch(
                    "aicage.registry.local_build.ensure_local_image.refresh_base_digest",
                    return_value="sha256:base",
                ),
                mock.patch(
                    "aicage.registry.local_build.ensure_local_image.run_build"
                ) as build_mock,
                mock.patch(
                    "aicage.registry.local_build.ensure_local_image.AgentVersionChecker"
                ) as checker_cls,
            ):
                checker_cls.return_value.get_version.return_value = "1.2.3"
                ensure_local_image_module.ensure_local_image(run_config)

            build_mock.assert_not_called()

    @staticmethod
    def _build_custom_run_config() -> RunConfig:
        images_metadata = ImagesMetadata(
            aicage_image=_ImageReleaseInfo(version="0.3.3"),
            aicage_image_base=_ImageReleaseInfo(version="0.3.3"),
            bases={
                "ubuntu": BaseMetadata(
                    from_image="ubuntu:latest",
                    base_image_distro="Ubuntu",
                    base_image_description="Default",
                )
            },
            agents={
                "claude": AgentMetadata(
                    agent_path="~/.claude",
                    agent_full_name="Claude Code",
                    agent_homepage="https://example.com",
                    build_local=True,
                    valid_bases={"ubuntu": "ghcr.io/aicage/aicage:claude-ubuntu"},
                    local_definition_dir=Path("/tmp/definition"),
                )
            },
        )
        return RunConfig(
            project_path=Path("/tmp/project"),
            agent="claude",
            context=ConfigContext(
                store=mock.Mock(),
                project_cfg=ProjectConfig(path="/tmp/project", agents={}),
                images_metadata=images_metadata,
                extensions={},
            ),
            selection=ImageSelection(
                image_ref="aicage:claude-ubuntu",
                base="ubuntu",
                extensions=[],
                base_image_ref="aicage:claude-ubuntu",
            ),
            project_docker_args="",
            mounts=[],
        )
