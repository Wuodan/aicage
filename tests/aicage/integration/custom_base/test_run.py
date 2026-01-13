from pathlib import Path

import pytest

from aicage.config.config_store import SettingsStore

from .._helpers import (
    copy_custom_base_sample,
    copy_forge_sample,
    custom_agents_dir,
    custom_bases_dir,
    require_integration,
    run_agent_version,
    setup_workspace,
)

pytestmark = pytest.mark.integration

_CUSTOM_BASE_NAME: str = "php"


@pytest.mark.parametrize(
    ("agent_name", "is_custom_agent"),
    [
        ("codex", False),
        ("claude", False),
        ("forge", True),
    ],
)
def test_custom_base_agents_run(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    agent_name: str,
    is_custom_agent: bool,
) -> None:
    require_integration()
    workspace, env = setup_workspace(monkeypatch, tmp_path, agent_name)
    base_dir = custom_bases_dir() / _CUSTOM_BASE_NAME
    base_dir.parent.mkdir(parents=True, exist_ok=True)
    copy_custom_base_sample(_CUSTOM_BASE_NAME, base_dir)
    if is_custom_agent:
        agent_dir = custom_agents_dir() / agent_name
        copy_forge_sample(agent_dir)
    _set_agent_base(workspace, agent_name, _CUSTOM_BASE_NAME)

    run_agent_version(env, workspace, agent_name)


def _set_agent_base(workspace: Path, agent_name: str, base_name: str) -> None:
    store = SettingsStore()
    project_cfg = store.load_project(workspace)
    agent_cfg = project_cfg.agents[agent_name]
    agent_cfg.base = base_name
    store.save_project(workspace, project_cfg)
