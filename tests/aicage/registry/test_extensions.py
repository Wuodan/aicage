import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.registry import _extended_images, _extensions


class ExtensionDiscoveryTests(TestCase):
    def test_load_extensions_reads_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            self._write_extension(extension_dir, name="Sample", description="Desc")
            with mock.patch(
                "aicage.registry._extensions.DEFAULT_CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                extensions = _extensions.load_extensions()

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
                "aicage.registry._extensions.DEFAULT_CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                extensions = _extensions.load_extensions()
                metadata = extensions["sample"]
                first_hash = _extensions.extension_hash(metadata)
                script_path = metadata.scripts_dir / "01-install.sh"
                script_path.write_text("#!/usr/bin/env bash\necho changed\n", encoding="utf-8")
                second_hash = _extensions.extension_hash(metadata)

        self.assertNotEqual(first_hash, second_hash)

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
                "aicage.registry._extended_images.DEFAULT_CUSTOM_EXTENDED_IMAGES_DIR",
                Path(images_dir),
            ):
                configs = _extended_images.load_extended_images(set())

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
                "aicage.registry._extended_images.DEFAULT_CUSTOM_EXTENDED_IMAGES_DIR",
                Path(images_dir),
            ):
                configs = _extended_images.load_extended_images({"marker"})

        self.assertIn("custom", configs)
        self.assertEqual("codex", configs["custom"].agent)

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
