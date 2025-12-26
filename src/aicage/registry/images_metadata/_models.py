from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import yaml

from aicage.errors import CliError


@dataclass(frozen=True)
class _ImageReleaseInfo:
    version: str


@dataclass(frozen=True)
class _BaseMetadata:
    root_image: str
    base_image_distro: str
    base_image_description: str
    os_installer: str
    test_suite: str


@dataclass(frozen=True)
class _ToolMetadata:
    tool_path: str
    tool_full_name: str
    tool_homepage: str
    valid_bases: list[str]
    base_exclude: list[str] | None = None
    base_distro_exclude: list[str] | None = None


@dataclass(frozen=True)
class ImagesMetadata:
    aicage_image: _ImageReleaseInfo
    aicage_image_base: _ImageReleaseInfo
    bases: dict[str, _BaseMetadata]
    tools: dict[str, _ToolMetadata]

    @classmethod
    def from_yaml(cls, payload: str) -> ImagesMetadata:
        try:
            data = yaml.safe_load(payload) or {}
        except yaml.YAMLError as exc:
            raise CliError(f"Invalid images metadata YAML: {exc}") from exc
        if not isinstance(data, dict):
            raise CliError("Images metadata YAML must be a mapping at the top level.")
        return cls.from_mapping(data)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> ImagesMetadata:
        _expect_keys(
            data,
            required={"aicage-image", "aicage-image-base", "bases", "tool"},
            optional=set(),
            context="images metadata",
        )
        aicage_image = _parse_release_info(data["aicage-image"], "aicage-image")
        aicage_image_base = _parse_release_info(data["aicage-image-base"], "aicage-image-base")
        bases = _parse_bases(data["bases"])
        tools = _parse_tools(data["tool"])
        return cls(
            aicage_image=aicage_image,
            aicage_image_base=aicage_image_base,
            bases=bases,
            tools=tools,
        )


def _parse_release_info(value: Any, context: str) -> _ImageReleaseInfo:
    mapping = _expect_mapping(value, context)
    _expect_keys(mapping, required={"version"}, optional=set(), context=context)
    return _ImageReleaseInfo(version=_expect_string(mapping.get("version"), f"{context}.version"))


def _parse_bases(value: Any) -> dict[str, _BaseMetadata]:
    mapping = _expect_mapping(value, "bases")
    bases: dict[str, _BaseMetadata] = {}
    for name, base_value in mapping.items():
        if not isinstance(name, str):
            raise CliError("Images metadata base keys must be strings.")
        base_mapping = _expect_mapping(base_value, f"bases.{name}")
        _expect_keys(
            base_mapping,
            required={
                "root_image",
                "base_image_distro",
                "base_image_description",
                "os_installer",
                "test_suite",
            },
            optional=set(),
            context=f"bases.{name}",
        )
        bases[name] = _BaseMetadata(
            root_image=_expect_string(base_mapping.get("root_image"), f"bases.{name}.root_image"),
            base_image_distro=_expect_string(
                base_mapping.get("base_image_distro"), f"bases.{name}.base_image_distro"
            ),
            base_image_description=_expect_string(
                base_mapping.get("base_image_description"),
                f"bases.{name}.base_image_description",
            ),
            os_installer=_expect_string(base_mapping.get("os_installer"), f"bases.{name}.os_installer"),
            test_suite=_expect_string(base_mapping.get("test_suite"), f"bases.{name}.test_suite"),
        )
    return bases


def _parse_tools(value: Any) -> dict[str, _ToolMetadata]:
    mapping = _expect_mapping(value, "tool")
    tools: dict[str, _ToolMetadata] = {}
    for name, tool_value in mapping.items():
        if not isinstance(name, str):
            raise CliError("Images metadata tool keys must be strings.")
        tool_mapping = _expect_mapping(tool_value, f"tool.{name}")
        _expect_keys(
            tool_mapping,
            required={"tool_path", "tool_full_name", "tool_homepage", "valid_bases"},
            optional={"base_exclude", "base_distro_exclude"},
            context=f"tool.{name}",
        )
        tools[name] = _ToolMetadata(
            tool_path=_expect_string(tool_mapping.get("tool_path"), f"tool.{name}.tool_path"),
            tool_full_name=_expect_string(
                tool_mapping.get("tool_full_name"), f"tool.{name}.tool_full_name"
            ),
            tool_homepage=_expect_string(
                tool_mapping.get("tool_homepage"), f"tool.{name}.tool_homepage"
            ),
            valid_bases=_expect_str_list(tool_mapping.get("valid_bases"), f"tool.{name}.valid_bases"),
            base_exclude=_maybe_str_list(tool_mapping.get("base_exclude"), f"tool.{name}.base_exclude"),
            base_distro_exclude=_maybe_str_list(
                tool_mapping.get("base_distro_exclude"), f"tool.{name}.base_distro_exclude"
            ),
        )
    return tools


def _expect_mapping(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CliError(f"{context} must be a mapping.")
    return value


def _expect_string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CliError(f"{context} must be a non-empty string.")
    return value


def _expect_str_list(value: Any, context: str) -> list[str]:
    if not isinstance(value, list):
        raise CliError(f"{context} must be a list.")
    items: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise CliError(f"{context} must contain non-empty strings.")
        items.append(item)
    return items


def _maybe_str_list(value: Any, context: str) -> list[str] | None:
    if value is None:
        return None
    return _expect_str_list(value, context)


def _expect_keys(
    mapping: dict[str, Any],
    required: set[str],
    optional: set[str],
    context: str,
) -> None:
    missing = sorted(required - set(mapping))
    if missing:
        raise CliError(f"{context} missing required keys: {', '.join(missing)}.")
    unknown = sorted(set(mapping) - required - optional)
    if unknown:
        raise CliError(f"{context} contains unsupported keys: {', '.join(unknown)}.")
