from pathlib import Path
from unittest import TestCase, mock

from aicage.config.context import ConfigContext
from aicage.config.images_metadata.models import (
    AgentMetadata,
    BaseMetadata,
    ImagesMetadata,
)
from aicage.config.project_config import ProjectConfig
from aicage.runtime.errors import RuntimeExecutionError
from aicage.runtime.prompts import BaseSelectionRequest, prompt_for_base
from aicage.runtime.prompts.base import available_bases, base_options


class PromptTests(TestCase):
    def test_prompt_for_base_validates_choice(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch(
            "builtins.input", return_value="fedora"
        ):
            with self.assertRaises(RuntimeExecutionError):
                prompt_for_base(
                    BaseSelectionRequest(
                        agent="codex",
                        context=self._build_context(["ubuntu"]),
                        agent_metadata=self._agent_metadata(["ubuntu"]),
                    )
                )

    def test_prompt_for_base_accepts_number_and_default(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", side_effect=["2", ""]):
            choice = prompt_for_base(
                BaseSelectionRequest(
                    agent="codex",
                    context=self._build_context(["alpine", "ubuntu"]),
                    agent_metadata=self._agent_metadata(["alpine", "ubuntu"]),
                )
            )
            self.assertEqual("ubuntu", choice)
            default_choice = prompt_for_base(
                BaseSelectionRequest(
                    agent="codex",
                    context=self._build_context(["ubuntu"]),
                    agent_metadata=self._agent_metadata(["ubuntu"]),
                )
            )
            self.assertEqual("ubuntu", default_choice)
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", return_value="3"):
            with self.assertRaises(RuntimeExecutionError):
                prompt_for_base(
                    BaseSelectionRequest(
                        agent="codex",
                        context=self._build_context(["alpine", "ubuntu"]),
                        agent_metadata=self._agent_metadata(["alpine", "ubuntu"]),
                    )
                )

    def test_prompt_for_base_accepts_default_without_list(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", return_value=""):
            choice = prompt_for_base(
                BaseSelectionRequest(
                    agent="codex",
                    context=self._build_context([]),
                    agent_metadata=self._agent_metadata([]),
                )
            )
        self.assertEqual("ubuntu", choice)

    def test_base_options_returns_descriptions(self) -> None:
        context = self._build_context(["ubuntu"])
        options = base_options(context, self._agent_metadata(["ubuntu"]))
        self.assertEqual([("ubuntu", "Default")], [(option.base, option.description) for option in options])

    def test_available_bases_returns_list(self) -> None:
        context = self._build_context(["ubuntu", "alpine"])
        options = base_options(context, self._agent_metadata(["ubuntu", "alpine"]))
        self.assertEqual(["alpine", "ubuntu"], available_bases(options))

    @staticmethod
    def _build_context(bases: list[str]) -> ConfigContext:
        metadata = PromptTests._metadata_with_bases(bases)
        return ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path="/tmp/project", agents={}),
            images_metadata=metadata,
            agents=metadata.agents,
            bases=metadata.bases,
            extensions={},
        )

    @staticmethod
    def _agent_metadata(bases: list[str]) -> AgentMetadata:
        metadata = PromptTests._metadata_with_bases(bases)
        return metadata.agents["codex"]

    @staticmethod
    def _metadata_with_bases(bases: list[str]) -> ImagesMetadata:
        base_entries = {
            name: BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro="Ubuntu",
                base_image_description="Default",
                build_local=False,
                local_definition_dir=Path(f"/tmp/{name}"),
            )
            for name in bases
        }
        agents = {
            "codex": AgentMetadata(
                agent_path="~/.codex",
                agent_full_name="Codex CLI",
                agent_homepage="https://example.com",
                build_local=False,
                valid_bases={name: f"repo:{name}" for name in bases},
                local_definition_dir=Path("/tmp/codex"),
            )
        }
        return ImagesMetadata(bases=base_entries, agents=agents)
