import tempfile
from pathlib import Path
from unittest import TestCase

from aicage.config.agent.models import AgentMetadata
from aicage.runtime._agent_config import resolve_agent_config


class AgentConfigTests(TestCase):
    def test_resolve_agent_config_reads_metadata_and_creates_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir) / ".codex"
            agents = {
                "codex": AgentMetadata(
                    agent_path=[str(agent_dir)],
                    agent_full_name="Codex CLI",
                    agent_homepage="https://example.com",
                    build_local=False,
                    valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                    local_definition_dir=Path("/tmp/agent"),
                )
            }
            config = resolve_agent_config(agents["codex"])
            self.assertEqual([str(agent_dir)], config.agent_path)
            self.assertTrue(config.agent_config_host[0].exists())

    def test_resolve_agent_config_creates_parent_for_file_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_file = Path(tmp_dir) / ".claude.json"
            agents = {
                "claude": AgentMetadata(
                    agent_path=[str(agent_file)],
                    agent_full_name="Claude Code",
                    agent_homepage="https://example.com",
                    build_local=False,
                    valid_bases={"ubuntu": "ghcr.io/aicage/aicage:claude-ubuntu"},
                    local_definition_dir=Path("/tmp/agent"),
                )
            }
            config = resolve_agent_config(agents["claude"])
            self.assertEqual([str(agent_file)], config.agent_path)
            self.assertTrue(config.agent_config_host[0].exists())
            self.assertTrue(config.agent_config_host[0].is_file())

    def test_resolve_agent_config_respects_existing_file_without_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_file = Path(tmp_dir) / "config"
            agent_file.write_text("data\n", encoding="utf-8")
            agents = {
                "plain": AgentMetadata(
                    agent_path=[str(agent_file)],
                    agent_full_name="Plain",
                    agent_homepage="https://example.com",
                    build_local=False,
                    valid_bases={"ubuntu": "ghcr.io/aicage/aicage:plain-ubuntu"},
                    local_definition_dir=Path("/tmp/agent"),
                )
            }
            config = resolve_agent_config(agents["plain"])
            self.assertTrue(config.agent_config_host[0].is_file())
