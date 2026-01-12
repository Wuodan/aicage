import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.images_metadata._base_discovery import discover_bases
from aicage.config.images_metadata.models import (
    _AGENT_KEY,
    _AICAGE_IMAGE_BASE_KEY,
    _AICAGE_IMAGE_KEY,
    _BASE_IMAGE_DESCRIPTION_KEY,
    _BASE_IMAGE_DISTRO_KEY,
    _BASES_KEY,
    _FROM_IMAGE_KEY,
    _OS_INSTALLER_KEY,
    _TEST_SUITE_KEY,
    _VALID_BASES_KEY,
    _VERSION_KEY,
    AGENT_FULL_NAME_KEY,
    AGENT_HOMEPAGE_KEY,
    AGENT_PATH_KEY,
    BASE_DISTRO_EXCLUDE_KEY,
    BASE_EXCLUDE_KEY,
    BUILD_LOCAL_KEY,
    ImagesMetadata,
)
from aicage.paths import CUSTOM_BASE_DEFINITION_FILES


class BaseDiscoveryTests(TestCase):
    def test_discover_bases_returns_release_metadata_when_missing_custom_dir(self) -> None:
        metadata = self._metadata_with_bases(["ubuntu"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing = Path(tmp_dir) / "missing-custom-bases"
            with mock.patch(
                "aicage.config.custom_base.loader.DEFAULT_CUSTOM_BASES_DIR",
                missing,
            ):
                discovered = discover_bases(metadata, "aicage")
        self.assertIs(discovered, metadata)

    def test_discover_bases_overrides_release_base(self) -> None:
        metadata = self._metadata_with_bases(["ubuntu"])
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
                "aicage.config.custom_base.loader.DEFAULT_CUSTOM_BASES_DIR",
                custom_dir,
            ):
                discovered = discover_bases(metadata, "aicage")

        base = discovered.bases["ubuntu"]
        self.assertEqual("Custom Debian", base.base_image_description)
        self.assertEqual("aicage:codex-ubuntu", discovered.agents["codex"].valid_bases["ubuntu"])

    def test_discover_bases_respects_excludes(self) -> None:
        metadata = self._metadata_with_bases(["ubuntu"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            custom_dir = Path(tmp_dir)
            custom_base = custom_dir / "custom"
            custom_base.mkdir()
            self._write_base_definition(
                custom_base,
                from_image="debian:latest",
                base_image_distro="CustomOS",
                base_image_description="Custom OS",
            )
            (custom_base / "Dockerfile").write_text("FROM ${FROM_IMAGE}\n", encoding="utf-8")
            fedora_base = custom_dir / "fedora"
            fedora_base.mkdir()
            self._write_base_definition(
                fedora_base,
                from_image="fedora:latest",
                base_image_distro="Fedora",
                base_image_description="Fedora custom",
            )
            (fedora_base / "Dockerfile").write_text("FROM ${FROM_IMAGE}\n", encoding="utf-8")
            with mock.patch(
                "aicage.config.custom_base.loader.DEFAULT_CUSTOM_BASES_DIR",
                custom_dir,
            ):
                discovered = discover_bases(metadata, "aicage")

        valid_bases = discovered.agents["codex"].valid_bases
        self.assertNotIn("custom", valid_bases)
        self.assertNotIn("fedora", valid_bases)

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
                    f"{_FROM_IMAGE_KEY}: {from_image}",
                    f"{_BASE_IMAGE_DISTRO_KEY}: {base_image_distro}",
                    f"{_BASE_IMAGE_DESCRIPTION_KEY}: {base_image_description}",
                ]
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _metadata_with_bases(bases: list[str]) -> ImagesMetadata:
        return ImagesMetadata.from_mapping(
            {
                _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
                _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
                _BASES_KEY: {
                    name: {
                        _FROM_IMAGE_KEY: "ubuntu:latest",
                        _BASE_IMAGE_DISTRO_KEY: name.capitalize(),
                        _BASE_IMAGE_DESCRIPTION_KEY: "Default",
                        _OS_INSTALLER_KEY: "distro/debian/install.sh",
                        _TEST_SUITE_KEY: "default",
                    }
                    for name in bases
                },
                _AGENT_KEY: {
                    "codex": {
                        AGENT_PATH_KEY: "~/.codex",
                        AGENT_FULL_NAME_KEY: "Codex CLI",
                        AGENT_HOMEPAGE_KEY: "https://example.com",
                        BUILD_LOCAL_KEY: False,
                        BASE_EXCLUDE_KEY: ["custom"],
                        BASE_DISTRO_EXCLUDE_KEY: ["fedora"],
                        _VALID_BASES_KEY: {
                            name: f"ghcr.io/aicage/aicage:codex-{name}" for name in bases
                        },
                    }
                },
            }
        )
