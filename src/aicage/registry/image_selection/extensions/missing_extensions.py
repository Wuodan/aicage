from pathlib import Path

from aicage.config.context import ConfigContext
from aicage.config.errors import ConfigError
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.project_config import AgentConfig
from aicage.config.yaml_loader import load_yaml
from aicage.registry.errors import RegistryError
from aicage.runtime.prompts import prompt_for_missing_extensions


def ensure_extensions_exist(
    agent: str,
    project_config_path: Path,
    agent_cfg: AgentConfig,
    extensions: dict[str, ExtensionMetadata],
    context: ConfigContext,
) -> bool:
    missing = [ext for ext in agent_cfg.extensions if ext not in extensions]
    if not missing:
        return False
    other_projects = _find_projects_using_image(context, agent_cfg.image_ref or "")
    choice = prompt_for_missing_extensions(
        agent=agent,
        missing=missing,
        stored_image_ref=agent_cfg.image_ref or "",
        project_config_path=project_config_path,
        other_projects=other_projects,
    )
    if choice == "fresh":
        context.project_cfg.agents.pop(agent, None)
        context.store.save_project(Path(context.project_cfg.path), context.project_cfg)
        return True
    if choice == "exit":
        raise RegistryError("Invalid extension configuration; run aborted.")
    raise RegistryError("Invalid choice; run aborted.")


def _find_projects_using_image(
    context: ConfigContext,
    image_ref: str,
) -> list[tuple[str, Path]]:
    if not image_ref:
        return []
    store = context.store
    matches: list[tuple[str, Path]] = []
    for path in sorted(store.projects_dir.glob("*.yaml")):
        data = _load_yaml(path)
        if not isinstance(data, dict):
            continue
        project_path = str(data.get("path", ""))
        agents = data.get("agents", {}) or {}
        if not isinstance(agents, dict):
            continue
        for cfg in agents.values():
            if isinstance(cfg, dict) and cfg.get("image_ref") == image_ref:
                matches.append((project_path, path))
                break
    return matches


def _load_yaml(path: Path) -> dict[str, object]:
    try:
        return load_yaml(path)
    except ConfigError:
        return {}
