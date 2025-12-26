import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.errors import CliError
from aicage.runtime.tool_config import resolve_tool_config


class FakeImage:
    def __init__(self, labels: dict[str, str]):
        self.labels = labels


class FakeImages:
    def __init__(self, image: FakeImage):
        self._image = image

    def get(self, image_ref: str) -> FakeImage:
        return self._image


class FakeClient:
    def __init__(self, image: FakeImage):
        self.images = FakeImages(image)


class ToolConfigTests(TestCase):
    def test_resolve_tool_config_reads_label_and_creates_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tool_dir = Path(tmp_dir) / ".codex"
            image = FakeImage(labels={"org.aicage.tool.tool_path": str(tool_dir)})
            with mock.patch(
                "aicage.runtime.tool_config.get_docker_client",
                return_value=FakeClient(image),
            ):
                config = resolve_tool_config("ghcr.io/aicage/aicage:codex-ubuntu-latest")
            self.assertEqual(str(tool_dir), config.tool_path)
            self.assertTrue(config.tool_config_host.exists())

    def test_resolve_tool_config_missing_label_raises(self) -> None:
        image = FakeImage(labels={})
        with mock.patch(
            "aicage.runtime.tool_config.get_docker_client",
            return_value=FakeClient(image),
        ):
            with self.assertRaises(CliError):
                resolve_tool_config("ghcr.io/aicage/aicage:codex-ubuntu-latest")
