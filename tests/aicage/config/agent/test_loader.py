import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.agent.loader import load_agents
from aicage.config.agent.models import AgentMetadata
from aicage.config.base.models import BaseMetadata


class AgentLoaderTests(TestCase):
    def test_load_agents_merges_custom_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            dockerfile = root / "agent-build" / "Dockerfile"
            dockerfile.parent.mkdir(parents=True)
            dockerfile.write_text("FROM scratch\n", encoding="utf-8")

            agent_dir = root / "agent-build" / "agents" / "codex"
            agent_dir.mkdir(parents=True)
            (agent_dir / "agent.yml").write_text(
                "\n".join(
                    [
                        "agent_path:",
                        "  - ~/.codex",
                        "agent_full_name: Codex",
                        "agent_homepage: https://example.com",
                        "build_local: false",
                    ]
                ),
                encoding="utf-8",
            )
            (agent_dir / "install.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
            (agent_dir / "version.sh").write_text("echo 1.0.0\n", encoding="utf-8")

            bases = {
                "ubuntu": BaseMetadata(
                    from_image="ubuntu:latest",
                    base_image_distro="Ubuntu",
                    base_image_description="Default",
                    build_local=False,
                    local_definition_dir=Path("/tmp/base"),
                )
            }
            custom_agent = AgentMetadata(
                agent_path=["~/.custom"],
                agent_full_name="Custom",
                agent_homepage="https://example.com",
                build_local=True,
                valid_bases={"ubuntu": "aicage:custom-ubuntu"},
                local_definition_dir=Path("/tmp/custom"),
            )
            with (
                mock.patch(
                    "aicage.config.agent.loader.find_packaged_path",
                    return_value=dockerfile,
                ),
                mock.patch(
                    "aicage.config.agent.loader.load_custom_agents",
                    return_value={"codex": custom_agent},
                ),
            ):
                agents = load_agents(bases)

        self.assertEqual(custom_agent, agents["codex"])
