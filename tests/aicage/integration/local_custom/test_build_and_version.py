import os
from pathlib import Path

import pytest

from aicage.config.config_store import SettingsStore
from aicage.config.project_config import AgentConfig, ProjectConfig
from aicage.registry.custom_agent.loader import DEFAULT_CUSTOM_AGENTS_DIR
from aicage.registry.local_build._store import BuildStore

from .._helpers import build_cli_env, copy_forge_sample, run_cli_pty

pytestmark = pytest.mark.integration


def _require_integration() -> None:
    if not os.environ.get("AICAGE_RUN_INTEGRATION"):
        pytest.skip("Set AICAGE_RUN_INTEGRATION=1 to run integration tests.")


def _setup_workspace(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, agent_name: str) -> tuple[Path, dict[str, str]]:
    home_dir = tmp_path / "home"
    workspace = tmp_path / "workspace"
    home_dir.mkdir()
    workspace.mkdir()
    monkeypatch.setenv("HOME", str(home_dir))
    monkeypatch.chdir(workspace)

    store = SettingsStore()
    project_cfg = ProjectConfig(
        path=str(workspace),
        agents={agent_name: AgentConfig(base="ubuntu")},
    )
    store.save_project(workspace, project_cfg)

    return workspace, build_cli_env(home_dir)


def test_custom_agent_build_and_version(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _require_integration()
    workspace, env = _setup_workspace(monkeypatch, tmp_path, "forge")
    agent_dir = Path(os.path.expanduser(DEFAULT_CUSTOM_AGENTS_DIR)) / "forge"
    copy_forge_sample(agent_dir)

    exit_code, output = run_cli_pty(["forge", "--version"], env=env, cwd=workspace)
    assert exit_code == 0, output
    output_lines = [line.strip() for line in output.splitlines() if line.strip()]
    assert output_lines
    assert output_lines[-1]

    record = BuildStore().load("forge", "ubuntu")
    assert record is not None
