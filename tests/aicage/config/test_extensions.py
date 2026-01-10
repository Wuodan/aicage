import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config import extended_images as extended_images_module
from aicage.config import extensions as extensions_module
from aicage.config._yaml import load_yaml
from aicage.config.extended_images import ExtendedImageConfig
from aicage.errors import CliError


class ExtensionDiscoveryTests(TestCase):
    def test_load_extensions_reads_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            self._write_extension(extension_dir, name="Sample", description="Desc")
            with mock.patch(
                "aicage.config.extensions.DEFAULT_CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                extensions = extensions_module.load_extensions()

        self.assertIn("sample", extensions)
        metadata = extensions["sample"]
        self.assertEqual("Sample", metadata.name)
        self.assertEqual("Desc", metadata.description)

    def test_extension_hash_changes_on_script_edit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            self._write_extension(extension_dir, name="Sample", description="Desc")
            with mock.patch(
                "aicage.config.extensions.DEFAULT_CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                extensions = extensions_module.load_extensions()
                metadata = extensions["sample"]
                first_hash = extensions_module.extension_hash(metadata)
                script_path = metadata.scripts_dir / "01-install.sh"
                script_path.write_text("#!/usr/bin/env bash\necho changed\n", encoding="utf-8")
                second_hash = extensions_module.extension_hash(metadata)

        self.assertNotEqual(first_hash, second_hash)

    def test_extension_hash_changes_on_dockerfile_edit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            self._write_extension(extension_dir, name="Sample", description="Desc")
            (extension_dir / "Dockerfile").write_text("FROM ubuntu:latest\n", encoding="utf-8")
            with mock.patch(
                "aicage.config.extensions.DEFAULT_CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                extensions = extensions_module.load_extensions()
                metadata = extensions["sample"]
                first_hash = extensions_module.extension_hash(metadata)
                (extension_dir / "Dockerfile").write_text("FROM ubuntu:22.04\n", encoding="utf-8")
                second_hash = extensions_module.extension_hash(metadata)

        self.assertNotEqual(first_hash, second_hash)

    def test_load_extensions_skips_non_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_root.mkdir(parents=True)
            (extension_root / "README.md").write_text("ignore", encoding="utf-8")
            with mock.patch(
                "aicage.config.extensions.DEFAULT_CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                extensions = extensions_module.load_extensions()

        self.assertEqual({}, extensions)

    def test_load_extensions_requires_scripts_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            extension_dir.mkdir(parents=True)
            (extension_dir / "extension.yml").write_text(
                "name: \"Sample\"\ndescription: \"Desc\"\n",
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extensions.DEFAULT_CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                with self.assertRaises(CliError):
                    extensions_module.load_extensions()

    def test_load_extensions_requires_definition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            scripts_dir = extension_dir / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            with mock.patch(
                "aicage.config.extensions.DEFAULT_CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                with self.assertRaises(CliError):
                    extensions_module.load_extensions()

    def test_load_extensions_rejects_invalid_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            scripts_dir = extension_dir / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            (extension_dir / "extension.yml").write_text(
                "- not-a-mapping\n",
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extensions.DEFAULT_CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                with self.assertRaises(CliError):
                    extensions_module.load_extensions()

    def test_load_extensions_reports_read_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing_path = Path(tmp_dir) / "missing.yaml"
            with self.assertRaises(CliError):
                load_yaml(missing_path)

    def test_load_extensions_rejects_unknown_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            scripts_dir = extension_dir / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            (extension_dir / "extension.yml").write_text(
                "\n".join(
                    [
                        "name: \"Sample\"",
                        "description: \"Desc\"",
                        "extra: true",
                    ]
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extensions.DEFAULT_CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                with self.assertRaises(CliError):
                    extensions_module.load_extensions()

    def test_load_extensions_rejects_blank_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            scripts_dir = extension_dir / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            (extension_dir / "extension.yml").write_text(
                "name: \"\"\ndescription: \"Desc\"\n",
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extensions.DEFAULT_CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                with self.assertRaises(CliError):
                    extensions_module.load_extensions()

    def test_load_extensions_requires_required_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            scripts_dir = extension_dir / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            (extension_dir / "extension.yml").write_text(
                "name: \"Sample\"\n",
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extensions.DEFAULT_CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                with self.assertRaises(CliError):
                    extensions_module.load_extensions()

    def test_load_extended_images_skips_missing_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images_dir = Path(tmp_dir) / "image-extended"
            config_dir = images_dir / "custom"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "image-extended.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "agent: codex",
                        "base: ubuntu",
                        "extensions:",
                        "  - missing",
                        "image_ref: aicage-extended:codex-ubuntu-missing",
                    ]
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extended_images.DEFAULT_CUSTOM_EXTENDED_IMAGES_DIR",
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
                "aicage.config.extended_images.DEFAULT_CUSTOM_EXTENDED_IMAGES_DIR",
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
                "\n".join(
                    [
                        "agent: codex",
                        "base: ubuntu",
                        "extensions:",
                        "  - marker",
                        "image_ref: aicage-extended:codex-ubuntu-marker",
                    ]
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extended_images.DEFAULT_CUSTOM_EXTENDED_IMAGES_DIR",
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
                "aicage.config.extended_images.DEFAULT_CUSTOM_EXTENDED_IMAGES_DIR",
                Path(images_dir),
            ):
                with self.assertRaises(CliError):
                    extended_images_module.load_extended_images(set())

    def test_load_extended_images_rejects_invalid_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images_dir = Path(tmp_dir) / "image-extended"
            config_dir = images_dir / "custom"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "image-extended.yaml"
            config_path.write_text("- not-a-mapping\n", encoding="utf-8")
            with mock.patch(
                "aicage.config.extended_images.DEFAULT_CUSTOM_EXTENDED_IMAGES_DIR",
                Path(images_dir),
            ):
                with self.assertRaises(CliError):
                    extended_images_module.load_extended_images({"marker"})

    def test_load_extended_images_reports_read_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing_path = Path(tmp_dir) / "missing.yaml"
            with self.assertRaises(CliError):
                load_yaml(missing_path)

    def test_load_extended_images_rejects_unknown_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images_dir = Path(tmp_dir) / "image-extended"
            config_dir = images_dir / "custom"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "image-extended.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "agent: codex",
                        "base: ubuntu",
                        "extensions: []",
                        "image_ref: aicage-extended:codex-ubuntu",
                        "extra: true",
                    ]
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extended_images.DEFAULT_CUSTOM_EXTENDED_IMAGES_DIR",
                Path(images_dir),
            ):
                with self.assertRaises(CliError):
                    extended_images_module.load_extended_images(set())

    def test_load_extended_images_rejects_blank_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images_dir = Path(tmp_dir) / "image-extended"
            config_dir = images_dir / "custom"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "image-extended.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "agent: \"\"",
                        "base: ubuntu",
                        "extensions: []",
                        "image_ref: aicage-extended:codex-ubuntu",
                    ]
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extended_images.DEFAULT_CUSTOM_EXTENDED_IMAGES_DIR",
                Path(images_dir),
            ):
                with self.assertRaises(CliError):
                    extended_images_module.load_extended_images(set())

    def test_load_extended_images_rejects_invalid_extensions_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images_dir = Path(tmp_dir) / "image-extended"
            config_dir = images_dir / "custom"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "image-extended.yaml"
            config_path.write_text(
                "\n".join(
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
                "aicage.config.extended_images.DEFAULT_CUSTOM_EXTENDED_IMAGES_DIR",
                Path(images_dir),
            ):
                with self.assertRaises(CliError):
                    extended_images_module.load_extended_images(set())

    def test_load_extended_images_rejects_blank_extension_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images_dir = Path(tmp_dir) / "image-extended"
            config_dir = images_dir / "custom"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "image-extended.yaml"
            config_path.write_text(
                "\n".join(
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
                "aicage.config.extended_images.DEFAULT_CUSTOM_EXTENDED_IMAGES_DIR",
                Path(images_dir),
            ):
                with self.assertRaises(CliError):
                    extended_images_module.load_extended_images(set())

    def test_load_extended_images_requires_required_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images_dir = Path(tmp_dir) / "image-extended"
            config_dir = images_dir / "custom"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "image-extended.yaml"
            config_path.write_text(
                "\n".join(
                    [
                        "agent: codex",
                        "base: ubuntu",
                        "extensions: []",
                    ]
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extended_images.DEFAULT_CUSTOM_EXTENDED_IMAGES_DIR",
                Path(images_dir),
            ):
                with self.assertRaises(CliError):
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

    @staticmethod
    def _write_extension(path: Path, *, name: str, description: str) -> None:
        scripts_dir = path / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        (path / "extension.yml").write_text(
            f"name: \"{name}\"\ndescription: \"{description}\"\n",
            encoding="utf-8",
        )
        (scripts_dir / "01-install.sh").write_text(
            "#!/usr/bin/env bash\necho ok\n",
            encoding="utf-8",
        )
