from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from aicage.config._yaml import expect_bool, maybe_str_list
from aicage.config._yaml import expect_keys as _expect_keys
from aicage.config._yaml import expect_string as _expect_string
from aicage.config.errors import ConfigError
from aicage.config.resources import find_packaged_path

_AICAGE_IMAGE_KEY: str = "aicage-image"
_AICAGE_IMAGE_BASE_KEY: str = "aicage-image-base"
_BASES_KEY: str = "bases"
_AGENT_KEY: str = "agent"

_VERSION_KEY: str = "version"

_FROM_IMAGE_KEY: str = "from_image"
_BASE_IMAGE_DISTRO_KEY: str = "base_image_distro"
_BASE_IMAGE_DESCRIPTION_KEY: str = "base_image_description"
_OS_INSTALLER_KEY: str = "os_installer"
_TEST_SUITE_KEY: str = "test_suite"

AGENT_PATH_KEY: str = "agent_path"
AGENT_FULL_NAME_KEY: str = "agent_full_name"
AGENT_HOMEPAGE_KEY: str = "agent_homepage"
BUILD_LOCAL_KEY: str = "build_local"
_VALID_BASES_KEY: str = "valid_bases"
BASE_EXCLUDE_KEY: str = "base_exclude"
BASE_DISTRO_EXCLUDE_KEY: str = "base_distro_exclude"


@dataclass(frozen=True)
class _ImageReleaseInfo:
    version: str


@dataclass(frozen=True)
class _BaseMetadata:
    from_image: str
    base_image_distro: str
    base_image_description: str
    os_installer: str
    test_suite: str


BaseMetadata = _BaseMetadata


@dataclass(frozen=True)
class AgentMetadata:
    agent_path: str
    agent_full_name: str
    agent_homepage: str
    build_local: bool
    valid_bases: dict[str, str]
    base_exclude: list[str] | None = None
    base_distro_exclude: list[str] | None = None
    local_definition_dir: Path | None = None


@dataclass(frozen=True)
class ImagesMetadata:
    aicage_image: _ImageReleaseInfo
    aicage_image_base: _ImageReleaseInfo
    bases: dict[str, BaseMetadata]
    agents: dict[str, AgentMetadata]

    @classmethod
    def from_yaml(cls, payload: str) -> ImagesMetadata:
        try:
            data = yaml.safe_load(payload) or {}
        except yaml.YAMLError as exc:
            raise ConfigError(f"Invalid images metadata YAML: {exc}") from exc
        if not isinstance(data, dict):
            raise ConfigError("Images metadata YAML must be a mapping at the top level.")
        return cls.from_mapping(data)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> ImagesMetadata:
        _expect_keys(
            data,
            required={_AICAGE_IMAGE_KEY, _AICAGE_IMAGE_BASE_KEY, _BASES_KEY, _AGENT_KEY},
            optional=set(),
            context="images metadata",
        )
        aicage_image = _parse_release_info(data[_AICAGE_IMAGE_KEY], _AICAGE_IMAGE_KEY)
        aicage_image_base = _parse_release_info(data[_AICAGE_IMAGE_BASE_KEY], _AICAGE_IMAGE_BASE_KEY)
        bases = _parse_bases(data[_BASES_KEY])
        agents = _parse_agents(data[_AGENT_KEY])
        return cls(
            aicage_image=aicage_image,
            aicage_image_base=aicage_image_base,
            bases=bases,
            agents=agents,
        )


def _parse_release_info(value: Any, context: str) -> _ImageReleaseInfo:
    mapping = _expect_mapping(value, context)
    _expect_keys(mapping, required={_VERSION_KEY}, optional=set(), context=context)
    return _ImageReleaseInfo(version=_expect_string(mapping.get(_VERSION_KEY), f"{context}.{_VERSION_KEY}"))


def _parse_bases(value: Any) -> dict[str, BaseMetadata]:
    mapping = _expect_mapping(value, _BASES_KEY)
    bases: dict[str, BaseMetadata] = {}
    for name, base_value in mapping.items():
        if not isinstance(name, str):
            raise ConfigError("Images metadata base keys must be strings.")
        base_mapping = _expect_mapping(base_value, f"{_BASES_KEY}.{name}")
        _expect_keys(
            base_mapping,
            required={
                _FROM_IMAGE_KEY,
                _BASE_IMAGE_DISTRO_KEY,
                _BASE_IMAGE_DESCRIPTION_KEY,
                _OS_INSTALLER_KEY,
                _TEST_SUITE_KEY,
            },
            optional=set(),
            context=f"{_BASES_KEY}.{name}",
        )
        bases[name] = _BaseMetadata(
            from_image=_expect_string(
                base_mapping.get(_FROM_IMAGE_KEY),
                f"{_BASES_KEY}.{name}.{_FROM_IMAGE_KEY}",
            ),
            base_image_distro=_expect_string(
                base_mapping.get(_BASE_IMAGE_DISTRO_KEY),
                f"{_BASES_KEY}.{name}.{_BASE_IMAGE_DISTRO_KEY}",
            ),
            base_image_description=_expect_string(
                base_mapping.get(_BASE_IMAGE_DESCRIPTION_KEY),
                f"{_BASES_KEY}.{name}.{_BASE_IMAGE_DESCRIPTION_KEY}",
            ),
            os_installer=_expect_string(
                base_mapping.get(_OS_INSTALLER_KEY),
                f"{_BASES_KEY}.{name}.{_OS_INSTALLER_KEY}",
            ),
            test_suite=_expect_string(
                base_mapping.get(_TEST_SUITE_KEY),
                f"{_BASES_KEY}.{name}.{_TEST_SUITE_KEY}",
            ),
        )
    return bases


def _parse_agents(value: Any) -> dict[str, AgentMetadata]:
    mapping = _expect_mapping(value, _AGENT_KEY)
    agents: dict[str, AgentMetadata] = {}
    for name, agent_value in mapping.items():
        if not isinstance(name, str):
            raise ConfigError("Images metadata agent keys must be strings.")
        agent_mapping = _expect_mapping(agent_value, f"{_AGENT_KEY}.{name}")
        _expect_keys(
            agent_mapping,
            required={
                AGENT_PATH_KEY,
                AGENT_FULL_NAME_KEY,
                AGENT_HOMEPAGE_KEY,
                BUILD_LOCAL_KEY,
                _VALID_BASES_KEY,
            },
            optional={BASE_EXCLUDE_KEY, BASE_DISTRO_EXCLUDE_KEY},
            context=f"{_AGENT_KEY}.{name}",
        )
        agents[name] = AgentMetadata(
            agent_path=_expect_string(
                agent_mapping.get(AGENT_PATH_KEY), f"{_AGENT_KEY}.{name}.{AGENT_PATH_KEY}"
            ),
            agent_full_name=_expect_string(
                agent_mapping.get(AGENT_FULL_NAME_KEY),
                f"{_AGENT_KEY}.{name}.{AGENT_FULL_NAME_KEY}",
            ),
            agent_homepage=_expect_string(
                agent_mapping.get(AGENT_HOMEPAGE_KEY),
                f"{_AGENT_KEY}.{name}.{AGENT_HOMEPAGE_KEY}",
            ),
            build_local=expect_bool(
                agent_mapping.get(BUILD_LOCAL_KEY), f"{_AGENT_KEY}.{name}.{BUILD_LOCAL_KEY}"
            ),
            local_definition_dir=_local_definition_dir(name),
            valid_bases=_expect_str_mapping(
                agent_mapping.get(_VALID_BASES_KEY), f"{_AGENT_KEY}.{name}.{_VALID_BASES_KEY}"
            ),
            base_exclude=maybe_str_list(
                agent_mapping.get(BASE_EXCLUDE_KEY), f"{_AGENT_KEY}.{name}.{BASE_EXCLUDE_KEY}"
            ),
            base_distro_exclude=maybe_str_list(
                agent_mapping.get(BASE_DISTRO_EXCLUDE_KEY),
                f"{_AGENT_KEY}.{name}.{BASE_DISTRO_EXCLUDE_KEY}",
            ),
        )
    return agents


def _local_definition_dir(agent_name: str) -> Path:
    dockerfile = find_packaged_path("agent-build/Dockerfile")
    return dockerfile.parent / "agents" / agent_name


def _expect_mapping(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigError(f"{context} must be a mapping.")
    return value


def _expect_str_mapping(value: Any, context: str) -> dict[str, str]:
    mapping = _expect_mapping(value, context)
    items: dict[str, str] = {}
    for key, item in mapping.items():
        if not isinstance(key, str) or not key.strip():
            raise ConfigError(f"{context} must contain non-empty string keys.")
        if not isinstance(item, str) or not item.strip():
            raise ConfigError(f"{context} must contain non-empty string values.")
        items[key] = item
    return items
