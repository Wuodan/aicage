from unittest import TestCase, mock

from aicage.config.global_config import GlobalConfig
from aicage.registry import _pull_decision


class PullDecisionTests(TestCase):
    def test_decide_pull_returns_true_when_local_missing(self) -> None:
        global_cfg = _global_config()
        with mock.patch(
            "aicage.registry._pull_decision.get_local_repo_digest",
            return_value=None,
        ):
            self.assertTrue(_pull_decision.decide_pull("image:tag", global_cfg))

    def test_decide_pull_returns_false_when_remote_unknown(self) -> None:
        global_cfg = _global_config()
        with (
            mock.patch(
                "aicage.registry._pull_decision.get_local_repo_digest",
                return_value="sha256:local",
            ),
            mock.patch(
                "aicage.registry._pull_decision.get_remote_digest",
                return_value=None,
            ),
        ):
            self.assertFalse(_pull_decision.decide_pull("image:tag", global_cfg))

    def test_decide_pull_returns_true_when_digests_differ(self) -> None:
        global_cfg = _global_config()
        with (
            mock.patch(
                "aicage.registry._pull_decision.get_local_repo_digest",
                return_value="sha256:local",
            ),
            mock.patch(
                "aicage.registry._pull_decision.get_remote_digest",
                return_value="sha256:remote",
            ),
        ):
            self.assertTrue(_pull_decision.decide_pull("image:tag", global_cfg))


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
