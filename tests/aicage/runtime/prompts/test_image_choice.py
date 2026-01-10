from pathlib import Path
from unittest import TestCase, mock

from aicage.config.context import ConfigContext
from aicage.config.global_config import GlobalConfig
from aicage.config.images_metadata.models import AgentMetadata, ImagesMetadata, _BaseMetadata, _ImageReleaseInfo
from aicage.config.project_config import ProjectConfig
from aicage.errors import CliError
from aicage.runtime.prompts.base import base_options
from aicage.runtime.prompts.image_choice import (
    ExtendedImageOption,
    ImageChoiceRequest,
    _build_image_options,
    _parse_image_choice_response,
    _render_image_prompt,
    prompt_for_image_choice,
)


class PromptImageChoiceTests(TestCase):
    def test_prompt_for_image_choice_defaults_to_base(self) -> None:
        context = self._context()
        request = ImageChoiceRequest(
            agent="codex",
            context=context,
            agent_metadata=self._agent_metadata(),
            extended_options=[],
        )
        with (
            mock.patch("aicage.runtime.prompts.image_choice.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value=""),
        ):
            choice = prompt_for_image_choice(request)
        self.assertEqual("base", choice.kind)
        self.assertEqual("ubuntu", choice.value)

    def test_prompt_for_image_choice_accepts_extended_by_number(self) -> None:
        context = self._context()
        extended = [
            ExtendedImageOption(
                name="custom",
                base="ubuntu",
                description="Custom",
                extensions=["ext"],
                image_ref="aicage-extended:custom",
            )
        ]
        request = ImageChoiceRequest(
            agent="codex",
            context=context,
            agent_metadata=self._agent_metadata(),
            extended_options=extended,
        )
        with (
            mock.patch("aicage.runtime.prompts.image_choice.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value="2"),
        ):
            choice = prompt_for_image_choice(request)
        self.assertEqual("extended", choice.kind)
        self.assertEqual("custom", choice.value)

    def test_prompt_for_image_choice_rejects_invalid(self) -> None:
        context = self._context()
        request = ImageChoiceRequest(
            agent="codex",
            context=context,
            agent_metadata=self._agent_metadata(),
            extended_options=[],
        )
        with (
            mock.patch("aicage.runtime.prompts.image_choice.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value="fedora"),
        ):
            with self.assertRaises(CliError):
                prompt_for_image_choice(request)

    def test_render_image_prompt_uses_default_when_no_options(self) -> None:
        request = ImageChoiceRequest(
            agent="codex",
            context=self._context(),
            agent_metadata=self._agent_metadata(),
            extended_options=[],
        )
        prompt = _render_image_prompt(request, [])
        self.assertEqual("Select image for 'codex' (runtime to use inside the container): [ubuntu]: ", prompt)

    def test_parse_image_choice_accepts_base_name(self) -> None:
        context = self._context()
        request = ImageChoiceRequest(
            agent="codex",
            context=context,
            agent_metadata=self._agent_metadata(),
            extended_options=[],
        )
        bases = base_options(context, request.agent_metadata)
        options = _build_image_options(bases, [])
        choice = _parse_image_choice_response("ubuntu", request, bases, [], options)
        self.assertEqual("base", choice.kind)
        self.assertEqual("ubuntu", choice.value)

    def test_parse_image_choice_accepts_extended_name(self) -> None:
        context = self._context()
        extended = [
            ExtendedImageOption(
                name="custom",
                base="ubuntu",
                description="Custom",
                extensions=["ext"],
                image_ref="aicage-extended:custom",
            )
        ]
        request = ImageChoiceRequest(
            agent="codex",
            context=context,
            agent_metadata=self._agent_metadata(),
            extended_options=extended,
        )
        bases = base_options(context, request.agent_metadata)
        options = _build_image_options(bases, extended)
        choice = _parse_image_choice_response("custom", request, bases, extended, options)
        self.assertEqual("extended", choice.kind)
        self.assertEqual("custom", choice.value)

    def test_parse_image_choice_rejects_invalid_number(self) -> None:
        context = self._context()
        request = ImageChoiceRequest(
            agent="codex",
            context=context,
            agent_metadata=self._agent_metadata(),
            extended_options=[],
        )
        bases = base_options(context, request.agent_metadata)
        options = _build_image_options(bases, [])
        with self.assertRaises(CliError):
            _parse_image_choice_response("99", request, bases, [], options)

    @staticmethod
    def _context() -> ConfigContext:
        return ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path="/tmp/project", agents={}),
            global_cfg=GlobalConfig(
                image_registry="ghcr.io",
                image_registry_api_url="https://ghcr.io/v2",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                image_repository="aicage/aicage",
                image_base_repository="aicage/aicage-image-base",
                default_image_base="ubuntu",
                version_check_image="ghcr.io/aicage/aicage-image-util:agent-version",
                local_image_repository="aicage",
                agents={},
            ),
            images_metadata=ImagesMetadata(
                aicage_image=_ImageReleaseInfo(version="0.3.3"),
                aicage_image_base=_ImageReleaseInfo(version="0.3.3"),
                bases={
                    "ubuntu": _BaseMetadata(
                        root_image="ubuntu:latest",
                        base_image_distro="Ubuntu",
                        base_image_description="Default",
                        os_installer="distro/debian/install.sh",
                        test_suite="default",
                    )
                },
                agents={},
            ),
        )

    @staticmethod
    def _agent_metadata() -> AgentMetadata:
        return AgentMetadata(
            agent_path="~/.codex",
            agent_full_name="Codex",
            agent_homepage="https://example.com",
            valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
            local_definition_dir=Path("/tmp/def"),
        )
