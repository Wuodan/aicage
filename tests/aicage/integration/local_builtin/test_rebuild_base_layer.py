import os
import subprocess
from pathlib import Path

import pytest

from aicage.config.config_store import SettingsStore
from aicage.config.project_config import AgentConfig, ProjectConfig
from aicage.registry.local_build._store import BuildStore

from .._helpers import build_cli_env, run_cli_pty

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


def _run_agent(env: dict[str, str], workspace: Path, agent_name: str) -> None:
    exit_code, output = run_cli_pty([agent_name, "--version"], env=env, cwd=workspace)
    assert exit_code == 0, output
    output_lines = [line.strip() for line in output.splitlines() if line.strip()]
    assert output_lines
    assert output_lines[-1]


def _replace_final_image(image_ref: str, tmp_path: Path) -> None:
    build_dir = tmp_path / "override"
    build_dir.mkdir(exist_ok=True)
    dockerfile = build_dir / "Dockerfile"
    dockerfile.write_text("FROM alpine:latest\nRUN echo replaced\n", encoding="utf-8")
    subprocess.run(
        [
            "docker",
            "build",
            "--no-cache",
            "--pull",
            "--tag",
            image_ref,
            str(build_dir),
        ],
        check=True,
        capture_output=True,
    )


def test_local_builtin_agent_rebuilds_on_base_layer(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _require_integration()
    workspace, env = _setup_workspace(monkeypatch, tmp_path, "claude")
    _run_agent(env, workspace, "claude")

    store = BuildStore()
    record = store.load("claude", "ubuntu")
    assert record is not None

    _replace_final_image(record.image_ref, tmp_path)
    _run_agent(env, workspace, "claude")
    updated = store.load("claude", "ubuntu")
    assert updated is not None
    assert updated.built_at != record.built_at
