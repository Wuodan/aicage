from pathlib import Path

import pytest

from aicage.config.config_store import SettingsStore
from aicage.config.project_config import AgentConfig
from aicage.registry.extension_build._extended_store import ExtendedBuildStore
from aicage.registry.local_build._store import BuildStore

from .._helpers import (
    assert_base_layer_present,
    copy_marker_extension_sample,
    custom_extensions_dir,
    force_record_agent_version,
    replace_final_image,
    require_integration,
    run_cli_pty,
    setup_workspace,
)

pytestmark = pytest.mark.integration


def test_local_builtin_extension_builds_and_runs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    require_integration()
    workspace, env = _setup_extension_workspace(monkeypatch, tmp_path, "claude")
    exit_code, output = _run_extension_check(env, workspace, "claude")
    assert exit_code == 0, output


def test_local_builtin_extension_rebuilds_on_agent_version(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    require_integration()
    workspace, env = _setup_extension_workspace(monkeypatch, tmp_path, "claude")
    exit_code, output = _run_extension_check(env, workspace, "claude")
    assert exit_code == 0, output

    store = BuildStore()
    record = store.load("claude", "ubuntu")
    assert record is not None
    force_record_agent_version(store, record, agent_version="0.0.0")

    exit_code, output = _run_extension_check(env, workspace, "claude")
    assert exit_code == 0, output
    updated = store.load("claude", "ubuntu")
    assert updated is not None
    assert updated.agent_version != "0.0.0"

    extended_record = ExtendedBuildStore().load("aicage-extended:claude-ubuntu-marker")
    assert extended_record is not None
    assert_base_layer_present(extended_record.base_image, extended_record.image_ref)


def test_local_builtin_extension_rebuilds_on_base_layer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    require_integration()
    workspace, env = _setup_extension_workspace(monkeypatch, tmp_path, "claude")
    exit_code, output = _run_extension_check(env, workspace, "claude")
    assert exit_code == 0, output

    extended_store = ExtendedBuildStore()
    record = extended_store.load("aicage-extended:claude-ubuntu-marker")
    assert record is not None

    replace_final_image(record.image_ref, tmp_path)

    exit_code, output = _run_extension_check(env, workspace, "claude")
    assert exit_code == 0, output
    assert_base_layer_present(record.base_image, record.image_ref)


def _setup_extension_workspace(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    agent_name: str,
) -> tuple[Path, dict[str, str]]:
    workspace, env = setup_workspace(
        monkeypatch,
        tmp_path,
        agent_name,
        docker_args="--entrypoint=/bin/sh",
    )
    extension_dir = custom_extensions_dir() / "marker"
    extension_dir.parent.mkdir(parents=True, exist_ok=True)
    copy_marker_extension_sample(extension_dir)

    store = SettingsStore()
    project_cfg = store.load_project(workspace)
    project_cfg.agents[agent_name] = AgentConfig(
        base="ubuntu",
        docker_args="--entrypoint=/bin/sh",
        image_ref=f"aicage-extended:{agent_name}-ubuntu-marker",
        extensions=["marker"],
    )
    store.save_project(workspace, project_cfg)
    return workspace, env


def _run_extension_check(env: dict[str, str], workspace: Path, agent_name: str) -> tuple[int, str]:
    return run_cli_pty(
        [agent_name, "-c", "test -f /usr/local/share/aicage-extensions/marker.txt"],
        env=env,
        cwd=workspace,
    )
