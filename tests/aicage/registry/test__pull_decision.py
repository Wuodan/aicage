from unittest import TestCase, mock

from aicage.registry import _pull_decision


class PullDecisionTests(TestCase):
    def test_decide_pull_returns_true_when_local_missing(self) -> None:
        with mock.patch(
            "aicage.registry._pull_decision.get_local_repo_digest",
            return_value=None,
        ):
            self.assertTrue(_pull_decision.decide_pull("image:tag"))

    def test_decide_pull_returns_false_when_remote_unknown(self) -> None:
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
            self.assertFalse(_pull_decision.decide_pull("image:tag"))

    def test_decide_pull_returns_true_when_digests_differ(self) -> None:
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
            self.assertTrue(_pull_decision.decide_pull("image:tag"))
