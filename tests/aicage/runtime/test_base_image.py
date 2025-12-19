import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config import GlobalConfig, ProjectConfig
from aicage.config.context import ConfigContext
from aicage.errors import CliError
from aicage.registry import image_selection
from aicage.registry.image_selection import ImageSelection


class BaseImageResolutionTests(TestCase):
    def test_resolve_uses_existing_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()
            tool_dir = Path(tmp_dir) / ".codex"
            context = ConfigContext(
                store=mock.Mock(),
                project_path=project_path,
                project_cfg=ProjectConfig(path=str(project_path), docker_args="", tools={}),
                global_cfg=GlobalConfig(
                    image_registry="ghcr.io",
                    image_registry_api_url="https://ghcr.io/v2",
                    image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                    image_repository="aicage/aicage",
                    default_image_base="ubuntu",
                    docker_args="",
                    tools={},
                ),
            )
            with mock.patch("aicage.registry.image_selection._pull_image"), mock.patch(
                "aicage.registry.image_selection._read_tool_label", return_value=str(tool_dir)
            ):
                context.project_cfg.tools["codex"] = {"base": "debian"}
                selection = image_selection.resolve_tool_image("codex", context)

            self.assertIsInstance(selection, ImageSelection)
            self.assertFalse(selection.project_dirty)
            self.assertEqual("ghcr.io/aicage/aicage:codex-debian-latest", selection.image_ref)
            self.assertEqual(tool_dir, selection.tool_config_host)

    def test_resolve_prompts_and_marks_dirty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()
            tool_dir = Path(tmp_dir) / ".codex"
            context = ConfigContext(
                store=mock.Mock(),
                project_path=project_path,
                project_cfg=ProjectConfig(path=str(project_path), docker_args="", tools={}),
                global_cfg=GlobalConfig(
                    image_registry="ghcr.io",
                    image_registry_api_url="https://ghcr.io/v2",
                    image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                    image_repository="aicage/aicage",
                    default_image_base="ubuntu",
                    docker_args="",
                    tools={},
                ),
            )
            with mock.patch(
                "aicage.registry.discovery.catalog.discover_tool_bases", return_value=["alpine", "ubuntu"]
            ), mock.patch(
                "aicage.registry.image_selection._pull_image"
            ), mock.patch(
                "aicage.registry.image_selection._read_tool_label", return_value=str(tool_dir)
            ), mock.patch(
                "aicage.registry.image_selection.prompt_for_base", return_value="alpine"
            ):
                selection = image_selection.resolve_tool_image("codex", context)

            self.assertTrue(selection.project_dirty)
            self.assertEqual("alpine", context.project_cfg.tools["codex"]["base"])
            self.assertEqual(tool_dir, selection.tool_config_host)

    def test_resolve_raises_without_bases(self) -> None:
        context = ConfigContext(
            store=mock.Mock(),
            project_path=Path("/tmp/project"),
            project_cfg=ProjectConfig(path="/tmp/project", docker_args="", tools={}),
            global_cfg=GlobalConfig(
                image_registry="ghcr.io",
                image_registry_api_url="https://ghcr.io/v2",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                image_repository="aicage/aicage",
                default_image_base="ubuntu",
                docker_args="",
                tools={},
            ),
        )
        with mock.patch("aicage.registry.discovery.catalog.discover_tool_bases", return_value=[]):
            with self.assertRaises(CliError):
                image_selection.resolve_tool_image("codex", context)
