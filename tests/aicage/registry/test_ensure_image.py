from unittest import TestCase, mock

from aicage.config.images_metadata.models import AgentMetadata
from aicage.config.runtime_config import RunConfig
from aicage.registry.ensure_image import ensure_image


class EnsureImageTests(TestCase):
    @staticmethod
    def test_ensure_image_pulls_when_not_local() -> None:
        run_config = _run_config(build_local=False, extensions=[])
        with (
            mock.patch("aicage.registry.ensure_image.pull_image") as pull_mock,
            mock.patch("aicage.registry.ensure_image.ensure_local_image") as local_mock,
            mock.patch("aicage.registry.ensure_image.ensure_extended_image") as extended_mock,
        ):
            ensure_image(run_config)

        pull_mock.assert_called_once()
        local_mock.assert_not_called()
        extended_mock.assert_not_called()

    @staticmethod
    def test_ensure_image_builds_local_when_custom_base() -> None:
        run_config = _run_config(
            build_local=False,
            extensions=[],
            base="custom",
            custom_bases={"custom": mock.Mock()},
        )
        with (
            mock.patch("aicage.registry.ensure_image.pull_image") as pull_mock,
            mock.patch("aicage.registry.ensure_image.ensure_local_image") as local_mock,
        ):
            ensure_image(run_config)

        pull_mock.assert_not_called()
        local_mock.assert_called_once_with(run_config)

    @staticmethod
    def test_ensure_image_runs_extended_build() -> None:
        run_config = _run_config(build_local=True, extensions=["extra"])
        with (
            mock.patch("aicage.registry.ensure_image.ensure_local_image") as local_mock,
            mock.patch("aicage.registry.ensure_image.ensure_extended_image") as extended_mock,
        ):
            ensure_image(run_config)

        local_mock.assert_called_once_with(run_config)
        extended_mock.assert_called_once_with(run_config)


def _run_config(
    build_local: bool,
    extensions: list[str],
    *,
    base: str = "ubuntu",
    custom_bases: dict[str, object] | None = None,
) -> RunConfig:
    run_config = mock.Mock(spec=RunConfig)
    run_config.agent = "codex"
    run_config.selection = mock.Mock()
    run_config.selection.base = base
    run_config.selection.base_image_ref = "ghcr.io/aicage/aicage:codex-ubuntu"
    run_config.selection.extensions = extensions
    run_config.context = mock.Mock()
    run_config.context.images_metadata = mock.Mock()
    run_config.context.custom_bases = custom_bases or {}
    run_config.context.images_metadata.agents = {
        "codex": AgentMetadata(
            agent_path="~/.custom",
            agent_full_name="Custom",
            agent_homepage="https://example.com",
            build_local=build_local,
            valid_bases={},
            local_definition_dir=None,
        )
    }
    return run_config
