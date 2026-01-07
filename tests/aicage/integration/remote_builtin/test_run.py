import os
from pathlib import Path

import pytest

from aicage.config.config_store import SettingsStore
from aicage.config.project_config import AgentConfig, ProjectConfig

from .._helpers import build_cli_env, run_cli_pty

pytestmark = pytest.mark.integration


def _require_integration() -> None:
    if not os.environ.get("AICAGE_RUN_INTEGRATION"):
        pytest.skip("Set AICAGE_RUN_INTEGRATION=1 to run integration tests.")


def _setup_workspace(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, agent_name: str) -> dict[str, str]:
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

    return build_cli_env(home_dir)


def test_builtin_agent_runs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _require_integration()
    env = _setup_workspace(monkeypatch, tmp_path, "codex")
    exit_code, output = run_cli_pty(["codex", "--version"], env=env, cwd=Path.cwd())
    assert exit_code == 0, output
    output_lines = [line.strip() for line in output.splitlines() if line.strip()]
    assert output_lines
    assert output_lines[-1]
