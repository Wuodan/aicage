import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config import ConfigError
from aicage.config import extended_images as extended_images_module
from aicage.config.extended_images import ExtendedImageConfig
from aicage.config.yaml_loader import load_yaml

from ._fixtures import extended_image_definition, join_yaml


class ExtendedImagesLoaderTests(TestCase):
    def test_extended_image_config_path(self) -> None:
        with mock.patch(
            "aicage.config.extended_images.IMAGE_EXTENDED_STATE_DIR",
            Path("/tmp/custom"),
        ):
            path = extended_images_module.extended_image_config_path("sample")

        self.assertEqual(Path("/tmp/custom/sample/image-extended.yaml"), path)

    def test_load_extended_images_skips_missing_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images_dir = Path(tmp_dir) / "image-extended"
            config_dir = images_dir / "custom"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "image-extended.yaml"
            config_path.write_text(
                extended_image_definition(
                    agent="codex",
                    base="ubuntu",
                    extensions=["missing"],
                    image_ref="aicage-extended:codex-ubuntu-missing",
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extended_images.IMAGE_EXTENDED_STATE_DIR",
                Path(images_dir),
            ):
                configs = extended_images_module.load_extended_images(set())

        self.assertEqual({}, configs)

    def test_load_extended_images_skips_non_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images_dir = Path(tmp_dir) / "image-extended"
            images_dir.mkdir(parents=True)
            (images_dir / "README.md").write_text("ignore", encoding="utf-8")
            with mock.patch(
                "aicage.config.extended_images.IMAGE_EXTENDED_STATE_DIR",
                Path(images_dir),
            ):
                configs = extended_images_module.load_extended_images(set())

        self.assertEqual({}, configs)

    def test_load_extended_images_reads_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images_dir = Path(tmp_dir) / "image-extended"
            config_dir = images_dir / "custom"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "image-extended.yaml"
            config_path.write_text(
                extended_image_definition(
                    agent="codex",
                    base="ubuntu",
                    extensions=["marker"],
                    image_ref="aicage-extended:codex-ubuntu-marker",
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extended_images.IMAGE_EXTENDED_STATE_DIR",
                Path(images_dir),
            ):
                configs = extended_images_module.load_extended_images({"marker"})

        self.assertIn("custom", configs)
        self.assertEqual("codex", configs["custom"].agent)

    def test_load_extended_images_requires_definition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images_dir = Path(tmp_dir) / "image-extended"
            config_dir = images_dir / "custom"
            config_dir.mkdir(parents=True)
            with mock.patch(
                "aicage.config.extended_images.IMAGE_EXTENDED_STATE_DIR",
                Path(images_dir),
            ):
                with self.assertRaises(ConfigError):
                    extended_images_module.load_extended_images(set())

    def test_load_extended_images_rejects_invalid_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images_dir = Path(tmp_dir) / "image-extended"
            config_dir = images_dir / "custom"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "image-extended.yaml"
            config_path.write_text("- not-a-mapping\n", encoding="utf-8")
            with mock.patch(
                "aicage.config.extended_images.IMAGE_EXTENDED_STATE_DIR",
                Path(images_dir),
            ):
                with self.assertRaises(ConfigError):
                    extended_images_module.load_extended_images({"marker"})

    def test_load_extended_images_reports_read_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing_path = Path(tmp_dir) / "missing.yaml"
            with self.assertRaises(ConfigError):
                load_yaml(missing_path)

    def test_load_extended_images_rejects_unknown_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images_dir = Path(tmp_dir) / "image-extended"
            config_dir = images_dir / "custom"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "image-extended.yaml"
            config_path.write_text(
                extended_image_definition(
                    agent="codex",
                    base="ubuntu",
                    extensions=[],
                    image_ref="aicage-extended:codex-ubuntu",
                    extra_lines=["extra: true"],
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extended_images.IMAGE_EXTENDED_STATE_DIR",
                Path(images_dir),
            ):
                with self.assertRaises(ConfigError):
                    extended_images_module.load_extended_images(set())

    def test_load_extended_images_rejects_blank_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images_dir = Path(tmp_dir) / "image-extended"
            config_dir = images_dir / "custom"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "image-extended.yaml"
            config_path.write_text(
                extended_image_definition(
                    agent="\"\"",
                    base="ubuntu",
                    extensions=[],
                    image_ref="aicage-extended:codex-ubuntu",
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extended_images.IMAGE_EXTENDED_STATE_DIR",
                Path(images_dir),
            ):
                with self.assertRaises(ConfigError):
                    extended_images_module.load_extended_images(set())

    def test_load_extended_images_rejects_invalid_extensions_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images_dir = Path(tmp_dir) / "image-extended"
            config_dir = images_dir / "custom"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "image-extended.yaml"
            config_path.write_text(
                join_yaml(
                    [
                        "agent: codex",
                        "base: ubuntu",
                        "extensions: invalid",
                        "image_ref: aicage-extended:codex-ubuntu",
                    ]
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extended_images.IMAGE_EXTENDED_STATE_DIR",
                Path(images_dir),
            ):
                with self.assertRaises(ConfigError):
                    extended_images_module.load_extended_images(set())

    def test_load_extended_images_rejects_blank_extension_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images_dir = Path(tmp_dir) / "image-extended"
            config_dir = images_dir / "custom"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "image-extended.yaml"
            config_path.write_text(
                join_yaml(
                    [
                        "agent: codex",
                        "base: ubuntu",
                        "extensions:",
                        "  - \"\"",
                        "image_ref: aicage-extended:codex-ubuntu",
                    ]
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extended_images.IMAGE_EXTENDED_STATE_DIR",
                Path(images_dir),
            ):
                with self.assertRaises(ConfigError):
                    extended_images_module.load_extended_images(set())

    def test_load_extended_images_requires_required_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images_dir = Path(tmp_dir) / "image-extended"
            config_dir = images_dir / "custom"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "image-extended.yaml"
            config_path.write_text(
                join_yaml(
                    [
                        "agent: codex",
                        "base: ubuntu",
                        "extensions: []",
                    ]
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extended_images.IMAGE_EXTENDED_STATE_DIR",
                Path(images_dir),
            ):
                with self.assertRaises(ConfigError):
                    extended_images_module.load_extended_images(set())

    def test_write_extended_image_config_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "custom" / "image-extended.yaml"
            config = ExtendedImageConfig(
                name="custom",
                agent="codex",
                base="ubuntu",
                extensions=["extra"],
                image_ref="aicage-extended:codex-ubuntu-extra",
                path=config_path,
            )
            extended_images_module.write_extended_image_config(config)

            payload = load_yaml(config_path)
            self.assertEqual("codex", payload.get("agent"))
            self.assertEqual(["extra"], payload.get("extensions"))
