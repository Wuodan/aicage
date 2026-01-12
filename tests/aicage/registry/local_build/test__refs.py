from unittest import TestCase, mock

from aicage.registry.local_build import _refs


class LocalBuildRefsTests(TestCase):
    def test_get_base_image_ref_uses_custom_base(self) -> None:
        run_config = mock.Mock()
        run_config.selection = mock.Mock()
        run_config.selection.base = "custom"
        with mock.patch("aicage.registry.local_build._refs.load_custom_base", return_value=mock.Mock()):
            ref = _refs.get_base_image_ref(run_config)

        self.assertEqual("aicage-image-base:custom", ref)

    def test_get_base_image_ref_uses_repository(self) -> None:
        run_config = mock.Mock()
        run_config.selection = mock.Mock()
        run_config.selection.base = "ubuntu"
        run_config.context = mock.Mock()
        run_config.context.global_cfg = mock.Mock()
        run_config.context.global_cfg.image_registry = "ghcr.io"
        run_config.context.global_cfg.image_base_repository = "aicage/aicage-image-base"
        with mock.patch("aicage.registry.local_build._refs.load_custom_base", return_value=None):
            ref = _refs.get_base_image_ref(run_config)

        self.assertEqual("ghcr.io/aicage/aicage-image-base:ubuntu", ref)

    def test_base_repository_includes_registry(self) -> None:
        run_config = mock.Mock()
        run_config.context = mock.Mock()
        run_config.context.global_cfg = mock.Mock()
        run_config.context.global_cfg.image_registry = "ghcr.io"
        run_config.context.global_cfg.image_base_repository = "aicage/aicage-image-base"

        repository = _refs.base_repository(run_config)

        self.assertEqual("ghcr.io/aicage/aicage-image-base", repository)
