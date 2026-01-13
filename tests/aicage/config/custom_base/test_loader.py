import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config import ConfigError
from aicage.config.custom_base.loader import _load_custom_base, load_custom_bases
from aicage.paths import CUSTOM_BASE_DEFINITION_FILES


class CustomBaseLoaderTests(TestCase):
    def test_load_custom_bases_returns_empty_when_missing_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing = Path(tmp_dir) / "missing-custom-bases"
            with mock.patch(
                "aicage.config.custom_base.loader.CUSTOM_BASES_DIR",
                missing,
            ):
                custom_bases = load_custom_bases()
        self.assertEqual({}, custom_bases)

    def test_load_custom_base_raises_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            custom_dir = Path(tmp_dir)
            with mock.patch(
                "aicage.config.custom_base.loader.CUSTOM_BASES_DIR",
                custom_dir,
            ):
                with self.assertRaises(ConfigError):
                    _load_custom_base("missing")

    def test_load_custom_bases_reads_definition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            custom_dir = Path(tmp_dir)
            base_dir = custom_dir / "ubuntu"
            base_dir.mkdir()
            self._write_base_definition(
                base_dir,
                from_image="debian:latest",
                base_image_distro="Debian",
                base_image_description="Custom Debian",
            )
            (base_dir / "Dockerfile").write_text("FROM ${FROM_IMAGE}\n", encoding="utf-8")
            with mock.patch(
                "aicage.config.custom_base.loader.CUSTOM_BASES_DIR",
                custom_dir,
            ):
                custom_bases = load_custom_bases()

        base = custom_bases["ubuntu"]
        self.assertEqual("debian:latest", base.from_image)
        self.assertEqual("Debian", base.base_image_distro)
        self.assertEqual("Custom Debian", base.base_image_description)

    def test_load_custom_bases_requires_dockerfile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            custom_dir = Path(tmp_dir)
            base_dir = custom_dir / "ubuntu"
            base_dir.mkdir()
            self._write_base_definition(
                base_dir,
                from_image="debian:latest",
                base_image_distro="Debian",
                base_image_description="Custom Debian",
            )
            with mock.patch(
                "aicage.config.custom_base.loader.CUSTOM_BASES_DIR",
                custom_dir,
            ):
                with self.assertRaises(ConfigError):
                    load_custom_bases()

    @staticmethod
    def _write_base_definition(
        base_dir: Path,
        *,
        from_image: str,
        base_image_distro: str,
        base_image_description: str,
    ) -> None:
        (base_dir / CUSTOM_BASE_DEFINITION_FILES[0]).write_text(
            "\n".join(
                [
                    f"from_image: {from_image}",
                    f"base_image_distro: {base_image_distro}",
                    f"base_image_description: {base_image_description}",
                ]
            ),
            encoding="utf-8",
        )
