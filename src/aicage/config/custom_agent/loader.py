from __future__ import annotations

from pathlib import Path
from typing import Any

from aicage.config._yaml import expect_bool, maybe_str_list
from aicage.config.errors import ConfigError
from aicage.config.image_refs import local_image_ref
from aicage.config.images_metadata.models import (
    AGENT_FULL_NAME_KEY,
    AGENT_HOMEPAGE_KEY,
    AGENT_PATH_KEY,
    BASE_DISTRO_EXCLUDE_KEY,
    BASE_EXCLUDE_KEY,
    BUILD_LOCAL_KEY,
    AgentMetadata,
    ImagesMetadata,
)
from aicage.config.yaml_loader import load_yaml
from aicage.constants import LOCAL_IMAGE_REPOSITORY
from aicage.paths import CUSTOM_AGENT_DEFINITION_FILES, CUSTOM_AGENTS_DIR

from ._validation import ensure_required_files, expect_string, validate_agent_mapping


def load_custom_agents(
    images_metadata: ImagesMetadata,
) -> dict[str, AgentMetadata]:
    agents_dir = CUSTOM_AGENTS_DIR
    if not agents_dir.is_dir():
        return {}

    custom_agents: dict[str, AgentMetadata] = {}
    for entry in sorted(agents_dir.iterdir()):
        if not entry.is_dir():
            continue
        agent_name = entry.name
        agent_path = _find_agent_definition(entry)
        agent_mapping = load_yaml(agent_path)
        ensure_required_files(agent_name, entry)
        custom_agents[agent_name] = _build_custom_agent(
            agent_name=agent_name,
            agent_mapping=agent_mapping,
            images_metadata=images_metadata,
        )
    return custom_agents


def _find_agent_definition(agent_dir: Path) -> Path:
    for filename in CUSTOM_AGENT_DEFINITION_FILES:
        candidate = agent_dir / filename
        if candidate.is_file():
            return candidate
    expected = ", ".join(CUSTOM_AGENT_DEFINITION_FILES)
    raise ConfigError(f"Custom agent '{agent_dir.name}' is missing {expected}.")


def _build_custom_agent(
    agent_name: str,
    agent_mapping: dict[str, Any],
    images_metadata: ImagesMetadata,
) -> AgentMetadata:
    normalized_mapping = validate_agent_mapping(agent_mapping)
    base_exclude = maybe_str_list(normalized_mapping.get(BASE_EXCLUDE_KEY), BASE_EXCLUDE_KEY)
    base_distro_exclude = maybe_str_list(
        normalized_mapping.get(BASE_DISTRO_EXCLUDE_KEY), BASE_DISTRO_EXCLUDE_KEY
    )
    build_local = expect_bool(normalized_mapping.get(BUILD_LOCAL_KEY), BUILD_LOCAL_KEY)
    valid_bases = _build_valid_bases(
        agent_name=agent_name,
        images_metadata=images_metadata,
        base_exclude=base_exclude,
        base_distro_exclude=base_distro_exclude,
    )
    return AgentMetadata(
        agent_path=expect_string(normalized_mapping.get(AGENT_PATH_KEY), AGENT_PATH_KEY),
        agent_full_name=expect_string(normalized_mapping.get(AGENT_FULL_NAME_KEY), AGENT_FULL_NAME_KEY),
        agent_homepage=expect_string(normalized_mapping.get(AGENT_HOMEPAGE_KEY), AGENT_HOMEPAGE_KEY),
        build_local=build_local,
        valid_bases=valid_bases,
        base_exclude=base_exclude,
        base_distro_exclude=base_distro_exclude,
        local_definition_dir=CUSTOM_AGENTS_DIR / agent_name,
    )


def _build_valid_bases(
    agent_name: str,
    images_metadata: ImagesMetadata,
    base_exclude: list[str] | None,
    base_distro_exclude: list[str] | None,
) -> dict[str, str]:
    valid_bases: dict[str, str] = {}
    base_exclude_set = _normalize_exclude(base_exclude)
    base_distro_exclude_set = _normalize_exclude(base_distro_exclude)
    for base_name in sorted(images_metadata.bases):
        base_metadata = images_metadata.bases[base_name]
        if _is_base_excluded(
            base_name,
            base_metadata.base_image_distro,
            base_exclude_set,
            base_distro_exclude_set,
        ):
            continue
        valid_bases[base_name] = local_image_ref(LOCAL_IMAGE_REPOSITORY, agent_name, base_name)
    return valid_bases


def _is_base_excluded(
    base_name: str,
    base_distro: str,
    base_exclude: set[str],
    base_distro_exclude: set[str],
) -> bool:
    base_name_lc = base_name.lower()
    if base_name_lc in base_exclude:
        return True
    if base_distro.lower() in base_distro_exclude:
        return True
    return False


def _normalize_exclude(values: list[str] | None) -> set[str]:
    if not values:
        return set()
    return {value.lower() for value in values}
