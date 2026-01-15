from aicage.config.agent.models import AgentMetadata
from aicage.config.context import ConfigContext


def filter_bases(context: ConfigContext, agent_metadata: AgentMetadata) -> set[str]:
    base_exclude = _normalize_exclude(agent_metadata.base_exclude)
    base_distro_exclude = _normalize_exclude(agent_metadata.base_distro_exclude)
    filtered: set[str] = set()
    for base_name, base_metadata in context.bases.items():
        if _is_base_excluded(
            base_name,
            base_metadata.base_image_distro,
            base_exclude,
            base_distro_exclude,
        ):
            continue
        filtered.add(base_name)
    return filtered


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
