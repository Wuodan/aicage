from __future__ import annotations

from aicage.config.image_refs import local_image_ref
from aicage.constants import LOCAL_IMAGE_REPOSITORY

from .models import AgentMetadata, BaseMetadata, ImagesMetadata


def discover_bases(
    images_metadata: ImagesMetadata,
    custom_bases: dict[str, BaseMetadata],
) -> ImagesMetadata:
    if not custom_bases:
        return images_metadata

    merged_bases = dict(images_metadata.bases)
    merged_bases.update(custom_bases)
    merged_agents = {
        name: _merge_agent_custom_bases(
            agent_name=name,
            agent_metadata=agent_metadata,
            custom_bases=custom_bases,
        )
        for name, agent_metadata in images_metadata.agents.items()
    }
    return ImagesMetadata(
        aicage_image=images_metadata.aicage_image,
        aicage_image_base=images_metadata.aicage_image_base,
        bases=merged_bases,
        agents=merged_agents,
    )


def _merge_agent_custom_bases(
    agent_name: str,
    agent_metadata: AgentMetadata,
    custom_bases: dict[str, BaseMetadata],
) -> AgentMetadata:
    valid_bases = dict(agent_metadata.valid_bases)
    base_exclude_set = _normalize_exclude(agent_metadata.base_exclude)
    base_distro_exclude_set = _normalize_exclude(agent_metadata.base_distro_exclude)
    for base_name, base_metadata in custom_bases.items():
        if _is_base_excluded(
            base_name,
            base_metadata.base_image_distro,
            base_exclude_set,
            base_distro_exclude_set,
        ):
            continue
        valid_bases[base_name] = local_image_ref(LOCAL_IMAGE_REPOSITORY, agent_name, base_name)
    return AgentMetadata(
        agent_path=agent_metadata.agent_path,
        agent_full_name=agent_metadata.agent_full_name,
        agent_homepage=agent_metadata.agent_homepage,
        build_local=agent_metadata.build_local,
        valid_bases=valid_bases,
        base_exclude=agent_metadata.base_exclude,
        base_distro_exclude=agent_metadata.base_distro_exclude,
        local_definition_dir=agent_metadata.local_definition_dir,
    )


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
