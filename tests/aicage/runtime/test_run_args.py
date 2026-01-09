from unittest import TestCase

from aicage.runtime.run_args import merge_docker_args


class RunArgsTests(TestCase):
    def test_merge_docker_args(self) -> None:
        merged = merge_docker_args("--one", "", "--two")
        self.assertEqual("--one --two", merged)
