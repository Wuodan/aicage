from unittest import TestCase

from aicage.config.image_refs import local_image_ref


class ImageRefsTests(TestCase):
    def test_local_image_ref_formats_tag(self) -> None:
        self.assertEqual("aicage:agent-ubuntu", local_image_ref("aicage", "Agent", "Ubuntu"))
        self.assertEqual("aicage:agent-sub-base", local_image_ref("aicage", "agent/sub", "base"))
