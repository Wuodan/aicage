import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.agent._custom_loader import load_custom_agents
from aicage.config.agent.models import (
    AGENT_FULL_NAME_KEY,
    AGENT_HOMEPAGE_KEY,
    AGENT_PATH_KEY,
    BASE_DISTRO_EXCLUDE_KEY,
    BASE_EXCLUDE_KEY,
)
from aicage.config.base.models import BaseMetadata
from aicage.config.errors import ConfigError
from aicage.paths import CUSTOM_AGENT_DEFINITION_FILES


class CustomAgentLoaderTests(TestCase):
    def test_load_custom_agents_returns_empty_when_missing_dir(self) -> None:
        bases = self._bases(["ubuntu"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing = Path(tmp_dir) / "missing-custom-agents"
            with mock.patch(
                "aicage.config.agent._custom_loader.CUSTOM_AGENTS_DIR",
                missing,
            ):
                custom_agents = load_custom_agents(bases)
        self.assertEqual({}, custom_agents)

    def test_load_custom_agents_builds_bases(self) -> None:
        bases = self._bases(["ubuntu", "fedora", "alpine"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            custom_dir = Path(tmp_dir)
            agent_dir = custom_dir / "custom"
            agent_dir.mkdir()
            (agent_dir / CUSTOM_AGENT_DEFINITION_FILES[0]).write_text(
                "\n".join(
                    [
                        f"{AGENT_PATH_KEY}: ~/.custom",
                        f"{AGENT_FULL_NAME_KEY}: Custom",
                        f"{AGENT_HOMEPAGE_KEY}: https://example.com",
                        f"{BASE_EXCLUDE_KEY}:",
                        "  - alpine",
                        f"{BASE_DISTRO_EXCLUDE_KEY}:",
                        "  - Fedora",
                    ]
                ),
                encoding="utf-8",
            )
            (agent_dir / "install.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
            (agent_dir / "version.sh").write_text("echo 1.0.0\n", encoding="utf-8")
            with mock.patch(
                "aicage.config.agent._custom_loader.CUSTOM_AGENTS_DIR",
                custom_dir,
            ):
                custom_agents = load_custom_agents(bases)

        agent = custom_agents["custom"]
        self.assertEqual(custom_dir / "custom", agent.local_definition_dir)
        self.assertEqual({"ubuntu": "aicage:custom-ubuntu"}, agent.valid_bases)

    def test_load_custom_agents_requires_install_and_version(self) -> None:
        bases = self._bases(["ubuntu"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            custom_dir = Path(tmp_dir)
            agent_dir = custom_dir / "custom"
            agent_dir.mkdir()
            (agent_dir / CUSTOM_AGENT_DEFINITION_FILES[0]).write_text(
                "\n".join(
                    [
                        f"{AGENT_PATH_KEY}: ~/.custom",
                        f"{AGENT_FULL_NAME_KEY}: Custom",
                        f"{AGENT_HOMEPAGE_KEY}: https://example.com",
                    ]
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.agent._custom_loader.CUSTOM_AGENTS_DIR",
                custom_dir,
            ):
                with self.assertRaises(ConfigError):
                    load_custom_agents(bases)

    @staticmethod
    def _bases(bases: list[str]) -> dict[str, BaseMetadata]:
        return {
            name: BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro=name.capitalize(),
                base_image_description="Default",
                build_local=False,
                local_definition_dir=Path(f"/tmp/{name}"),
            )
            for name in bases
        }
