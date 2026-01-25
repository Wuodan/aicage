import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.base.loader import load_bases
from aicage.config.base.models import BaseMetadata


class BaseLoaderTests(TestCase):
    def test_load_bases_merges_custom_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            dockerfile = root / "agent-build" / "Dockerfile"
            dockerfile.parent.mkdir(parents=True)
            dockerfile.write_text("FROM scratch\n", encoding="utf-8")

            ubuntu_dir = root / "base-build" / "bases" / "ubuntu"
            ubuntu_dir.mkdir(parents=True)
            (ubuntu_dir / "base.yml").write_text(
                "\n".join(
                    [
                        "from_image: ubuntu:latest",
                        "base_image_distro: Ubuntu",
                        "base_image_description: Default",
                    ]
                ),
                encoding="utf-8",
            )

            debian_dir = root / "base-build" / "bases" / "debian"
            debian_dir.mkdir(parents=True)
            (debian_dir / "base.yml").write_text(
                "\n".join(
                    [
                        "from_image: debian:latest",
                        "base_image_distro: Debian",
                        "base_image_description: Default",
                    ]
                ),
                encoding="utf-8",
            )

            custom_base = BaseMetadata(
                from_image="custom:latest",
                base_image_distro="Custom",
                base_image_description="Custom base",
                build_local=True,
                local_definition_dir=Path("/tmp/custom"),
            )
            with (
                mock.patch(
                    "aicage.config.base.loader.find_packaged_path",
                    return_value=dockerfile,
                ),
                mock.patch(
                    "aicage.config.base.loader.load_custom_bases",
                    return_value={"ubuntu": custom_base},
                ),
            ):
                bases = load_bases()

        self.assertEqual(custom_base, bases["ubuntu"])
        self.assertFalse(bases["debian"].build_local)
