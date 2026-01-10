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
            should_build = _plan.should_build(
                run_config,
                None,
                "ghcr.io/aicage/aicage-image-base:ubuntu",
                "1.2.3",
                run_config.image_ref,
            )
        self.assertTrue(should_build)

    def test_should_build_when_record_missing(self) -> None:
        run_config = build_run_config()
        with mock.patch(
            "aicage.registry.local_build._plan.local_image_exists",
            return_value=True,
        ):
            should_build = _plan.should_build(
                run_config,
                None,
                "ghcr.io/aicage/aicage-image-base:ubuntu",
                "1.2.3",
                run_config.image_ref,
            )
        self.assertTrue(should_build)

    def test_should_build_when_agent_version_changes(self) -> None:
        run_config = build_run_config()
        record = BuildRecord(
            agent="claude",
            base="ubuntu",
            agent_version="1.2.2",
            base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
            image_ref="aicage:claude-ubuntu",
            built_at="2024-01-01T00:00:00+00:00",
        )
        with (
            mock.patch(
                "aicage.registry.local_build._plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.local_build._plan.base_layer_missing",
                return_value=False,
            ),
        ):
            should_build = _plan.should_build(
                run_config,
                record,
                "ghcr.io/aicage/aicage-image-base:ubuntu",
                "1.2.3",
                run_config.image_ref,
            )
        self.assertTrue(should_build)

    def test_should_build_when_base_layer_missing(self) -> None:
        run_config = build_run_config()
        record = BuildRecord(
            agent="claude",
            base="ubuntu",
            agent_version="1.2.3",
            base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
            image_ref="aicage:claude-ubuntu",
            built_at="2024-01-01T00:00:00+00:00",
        )
        with (
            mock.patch(
                "aicage.registry.local_build._plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.local_build._plan.base_layer_missing",
                return_value=True,
            ),
        ):
            should_build = _plan.should_build(
                run_config,
                record,
                "ghcr.io/aicage/aicage-image-base:ubuntu",
                "1.2.3",
                run_config.image_ref,
            )
        self.assertTrue(should_build)

    def test_should_build_skips_when_layer_data_missing(self) -> None:
        run_config = build_run_config()
        record = BuildRecord(
            agent="claude",
            base="ubuntu",
            agent_version="1.2.3",
            base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
            image_ref="aicage:claude-ubuntu",
            built_at="2024-01-01T00:00:00+00:00",
        )
        with (
            mock.patch(
                "aicage.registry.local_build._plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.local_build._plan.base_layer_missing",
                return_value=None,
            ),
        ):
            should_build = _plan.should_build(
                run_config,
                record,
                "ghcr.io/aicage/aicage-image-base:ubuntu",
                "1.2.3",
                run_config.image_ref,
            )
        self.assertFalse(should_build)

    def test_should_build_false_when_up_to_date(self) -> None:
        run_config = build_run_config()
        record = BuildRecord(
            agent="claude",
            base="ubuntu",
            agent_version="1.2.3",
            base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
            image_ref="aicage:claude-ubuntu",
            built_at="2024-01-01T00:00:00+00:00",
        )
        with (
            mock.patch(
                "aicage.registry.local_build._plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.local_build._plan.base_layer_missing",
                return_value=False,
            ),
        ):
            should_build = _plan.should_build(
                run_config,
                record,
                "ghcr.io/aicage/aicage-image-base:ubuntu",
                "1.2.3",
                run_config.image_ref,
            )
        self.assertFalse(should_build)
