from unittest import TestCase, mock

from aicage.registry.local_build import _plan
from aicage.registry.local_build._store import BuildRecord

from ._fixtures import build_run_config


class LocalBuildPlanTests(TestCase):
    def test_should_build_when_missing_local_image(self) -> None:
        run_config = build_run_config()
        with mock.patch(
            "aicage.registry.local_build._plan.local_image_exists",
            return_value=False,
        ):
            should_build = _plan.should_build(run_config, None, "sha256:base")
        self.assertTrue(should_build)

    def test_should_build_when_record_missing(self) -> None:
        run_config = build_run_config()
        with mock.patch(
            "aicage.registry.local_build._plan.local_image_exists",
            return_value=True,
        ):
            should_build = _plan.should_build(run_config, None, "sha256:base")
        self.assertTrue(should_build)

    def test_should_build_when_agent_version_changes(self) -> None:
        run_config = build_run_config()
        record = BuildRecord(
            agent="claude",
            base="ubuntu",
            agent_version="1.2.2",
            base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
            base_digest="sha256:base",
            image_ref="aicage:claude-ubuntu",
            built_at="2024-01-01T00:00:00+00:00",
        )
        with mock.patch(
            "aicage.registry.local_build._plan.local_image_exists",
            return_value=True,
        ):
            should_build = _plan.should_build(run_config, record, "sha256:base")
        self.assertTrue(should_build)

    def test_should_build_when_record_missing_digest(self) -> None:
        run_config = build_run_config()
        record = BuildRecord(
            agent="claude",
            base="ubuntu",
            agent_version="1.2.3",
            base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
            base_digest=None,
            image_ref="aicage:claude-ubuntu",
            built_at="2024-01-01T00:00:00+00:00",
        )
        with mock.patch(
            "aicage.registry.local_build._plan.local_image_exists",
            return_value=True,
        ):
            should_build = _plan.should_build(run_config, record, "sha256:base")
        self.assertTrue(should_build)

    def test_should_build_when_base_digest_changes(self) -> None:
        run_config = build_run_config()
        record = BuildRecord(
            agent="claude",
            base="ubuntu",
            agent_version="1.2.3",
            base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
            base_digest="sha256:old",
            image_ref="aicage:claude-ubuntu",
            built_at="2024-01-01T00:00:00+00:00",
        )
        with mock.patch(
            "aicage.registry.local_build._plan.local_image_exists",
            return_value=True,
        ):
            should_build = _plan.should_build(run_config, record, "sha256:new")
        self.assertTrue(should_build)

    def test_should_build_false_when_up_to_date(self) -> None:
        run_config = build_run_config()
        record = BuildRecord(
            agent="claude",
            base="ubuntu",
            agent_version="1.2.3",
            base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
            base_digest="sha256:base",
            image_ref="aicage:claude-ubuntu",
            built_at="2024-01-01T00:00:00+00:00",
        )
        with mock.patch(
            "aicage.registry.local_build._plan.local_image_exists",
            return_value=True,
        ):
            should_build = _plan.should_build(run_config, record, "sha256:base")
        self.assertFalse(should_build)
