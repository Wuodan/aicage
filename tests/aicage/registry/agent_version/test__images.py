import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.global_config import GlobalConfig
from aicage.registry.agent_version import _images


class AgentVersionImagesTests(TestCase):
    def test_version_check_pulls_when_local_missing(self) -> None:
        global_cfg = self._global_config()
        image_ref = global_cfg.version_check_image
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry.agent_version._images.get_local_repo_digest",
                    return_value=None,
                ) as local_mock,
                mock.patch("aicage.registry.agent_version._images.get_remote_repo_digest") as remote_mock,
                mock.patch("aicage.registry.agent_version._images.run_pull") as pull_mock,
                mock.patch(
                    "aicage.registry.agent_version._images.pull_log_path",
                    return_value=log_path,
                ),
            ):
                _images.ensure_version_check_image(
                    image_ref=image_ref,
                    global_cfg=global_cfg,
                    logger=mock.Mock(),
                )
        local_mock.assert_called_once()
        remote_mock.assert_not_called()
        pull_mock.assert_called_once_with(image_ref, log_path)

    def test_version_check_skips_pull_when_remote_unknown(self) -> None:
        global_cfg = self._global_config()
        image_ref = global_cfg.version_check_image
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry.agent_version._images.get_local_repo_digest",
                    return_value="sha256:local",
                ),
                mock.patch(
                    "aicage.registry.agent_version._images.get_remote_repo_digest",
                    return_value=None,
                ) as remote_mock,
                mock.patch("aicage.registry.agent_version._images.run_pull") as pull_mock,
                mock.patch(
                    "aicage.registry.agent_version._images.pull_log_path",
                    return_value=log_path,
                ),
            ):
                _images.ensure_version_check_image(
                    image_ref=image_ref,
                    global_cfg=global_cfg,
                    logger=mock.Mock(),
                )
        remote_mock.assert_called_once()
        pull_mock.assert_not_called()

    @staticmethod
    def _global_config() -> GlobalConfig:
        return GlobalConfig(
            image_registry="ghcr.io",
            image_registry_api_url="https://ghcr.io/v2",
            image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
            image_repository="aicage/aicage",
            image_base_repository="aicage/aicage-image-base",
            default_image_base="ubuntu",
            version_check_image="ghcr.io/aicage/aicage-image-util:agent-version",
            local_image_repository="aicage",
            agents={},
        )
