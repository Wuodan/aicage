from pathlib import Path
from typing import Any

from aicage.config._yaml import expect_bool, expect_string, maybe_str_list
from aicage.config.agent._validation import validate_agent_mapping
from aicage.config.agent.models import (
    AGENT_FULL_NAME_KEY,
    AGENT_HOMEPAGE_KEY,
    AGENT_PATH_KEY,
    BASE_DISTRO_EXCLUDE_KEY,
    BASE_EXCLUDE_KEY,
    BUILD_LOCAL_KEY,
    AgentMetadata,
)
from aicage.config.base.models import BaseMetadata
from aicage.config.image_refs import local_image_ref
from aicage.constants import IMAGE_REGISTRY, IMAGE_REPOSITORY, LOCAL_IMAGE_REPOSITORY


def build_agent_metadata(
    agent_name: str,
    agent_mapping: dict[str, Any],
    bases: dict[str, BaseMetadata],
    definition_dir: Path,
) -> AgentMetadata:
    normalized_mapping = validate_agent_mapping(agent_mapping)
    base_exclude = maybe_str_list(normalized_mapping.get(BASE_EXCLUDE_KEY), BASE_EXCLUDE_KEY) or []
    base_distro_exclude = (
        maybe_str_list(normalized_mapping.get(BASE_DISTRO_EXCLUDE_KEY), BASE_DISTRO_EXCLUDE_KEY)
        or []
    )
    build_local = expect_bool(normalized_mapping.get(BUILD_LOCAL_KEY), BUILD_LOCAL_KEY)
    valid_bases = _build_valid_bases(
        agent_name=agent_name,
        bases=bases,
        base_exclude=base_exclude,
        base_distro_exclude=base_distro_exclude,
        build_local=build_local,
    )
    return AgentMetadata(
        agent_path=expect_string(normalized_mapping.get(AGENT_PATH_KEY), AGENT_PATH_KEY),
        agent_full_name=expect_string(normalized_mapping.get(AGENT_FULL_NAME_KEY), AGENT_FULL_NAME_KEY),
        agent_homepage=expect_string(normalized_mapping.get(AGENT_HOMEPAGE_KEY), AGENT_HOMEPAGE_KEY),
        build_local=build_local,
        valid_bases=valid_bases,
        base_exclude=base_exclude,
        base_distro_exclude=base_distro_exclude,
        local_definition_dir=definition_dir,
    )


def _build_valid_bases(
    agent_name: str,
    bases: dict[str, BaseMetadata],
    base_exclude: list[str],
    base_distro_exclude: list[str],
    build_local: bool,
) -> dict[str, str]:
    valid_bases: dict[str, str] = {}
    base_exclude_set = _normalize_exclude(base_exclude)
    base_distro_exclude_set = _normalize_exclude(base_distro_exclude)
    repository = _image_repository(build_local)
    for base_name in sorted(bases):
        base_metadata = bases[base_name]
        if _is_base_excluded(
            base_name,
            base_metadata.base_image_distro,
            base_exclude_set,
            base_distro_exclude_set,
        ):
            continue
        valid_bases[base_name] = local_image_ref(repository, agent_name, base_name)
    return valid_bases


def _image_repository(build_local: bool) -> str:
    if build_local:
        return LOCAL_IMAGE_REPOSITORY
    return f"{IMAGE_REGISTRY}/{IMAGE_REPOSITORY}"


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


def _normalize_exclude(values: list[str]) -> set[str]:
    if not values:
        return set()
    return {value.lower() for value in values}
