import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.registry.custom_agent.loader import load_custom_agents
from aicage.registry.images_metadata.models import ImagesMetadata


class CustomAgentLoaderTests(TestCase):
    def test_load_custom_agents_returns_empty_when_missing_dir(self) -> None:
        metadata = self._metadata_with_bases(["ubuntu"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing = Path(tmp_dir) / "missing-custom-agents"
            with mock.patch(
                "aicage.registry.custom_agent.loader.DEFAULT_CUSTOM_AGENTS_DIR",
                str(missing),
            ):
                custom_agents = load_custom_agents(metadata, "aicage")
        self.assertEqual({}, custom_agents)

    def test_load_custom_agents_builds_bases(self) -> None:
        metadata = self._metadata_with_bases(["ubuntu", "fedora", "alpine"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            custom_dir = Path(tmp_dir)
            agent_dir = custom_dir / "custom"
            agent_dir.mkdir()
            (agent_dir / "agent.yml").write_text(
                "\n".join(
                    [
                        "agent_path: ~/.custom",
                        "agent_full_name: Custom",
                        "agent_homepage: https://example.com",
                        "redistributable: false",
                        "base_exclude:",
                        "  - alpine",
                        "base_distro_exclude:",
                        "  - Fedora",
                    ]
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.registry.custom_agent.loader.DEFAULT_CUSTOM_AGENTS_DIR",
                str(custom_dir),
            ):
                custom_agents = load_custom_agents(metadata, "aicage")

        agent = custom_agents["custom"]
        self.assertTrue(agent.is_custom)
        self.assertEqual({"ubuntu": "aicage:custom-ubuntu"}, agent.valid_bases)

    @staticmethod
    def _metadata_with_bases(bases: list[str]) -> ImagesMetadata:
        return ImagesMetadata.from_mapping(
            {
                "aicage-image": {"version": "0.3.3"},
                "aicage-image-base": {"version": "0.3.3"},
                "bases": {
                    name: {
                        "root_image": "ubuntu:latest",
                        "base_image_distro": name.capitalize(),
                        "base_image_description": "Default",
                        "os_installer": "distro/debian/install.sh",
                        "test_suite": "default",
                    }
                    for name in bases
                },
                "agent": {
                    "codex": {
                        "agent_path": "~/.codex",
                        "agent_full_name": "Codex CLI",
                        "agent_homepage": "https://example.com",
                        "redistributable": True,
                        "valid_bases": {
                            name: f"ghcr.io/aicage/aicage:codex-{name}" for name in bases
                        },
                    }
                },
            }
        )
