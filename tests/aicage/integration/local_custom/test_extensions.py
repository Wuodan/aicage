from pathlib import Path

import pytest

from aicage.config.config_store import SettingsStore
from aicage.config.project_config import AgentConfig
from aicage.paths import DEFAULT_EXTENDED_IMAGE_NAME
from aicage.registry.extension_build._extended_store import ExtendedBuildStore
from aicage.registry.local_build._store import BuildStore

from .._helpers import (
    assert_base_layer_present,
    copy_forge_sample,
    copy_marker_extension_sample,
    custom_agents_dir,
    custom_extensions_dir,
    force_record_agent_version,
    replace_final_image,
    require_integration,
    run_cli_pty,
    setup_workspace,
)

pytestmark = pytest.mark.integration


def test_local_custom_extension_builds_and_runs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    require_integration()
    workspace, env = _setup_extension_workspace(monkeypatch, tmp_path)
    exit_code, output = _run_extension_check(env, workspace)
    assert exit_code == 0, output


def test_local_custom_extension_rebuilds_on_agent_version(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    require_integration()
    workspace, env = _setup_extension_workspace(monkeypatch, tmp_path)
    exit_code, output = _run_extension_check(env, workspace)
    assert exit_code == 0, output

    store = BuildStore()
    record = store.load("forge", "ubuntu")
    assert record is not None
    force_record_agent_version(store, record, agent_version="0.0.0")

    exit_code, output = _run_extension_check(env, workspace)
    assert exit_code == 0, output
    updated = store.load("forge", "ubuntu")
    assert updated is not None
    assert updated.agent_version != "0.0.0"

    extended_record = ExtendedBuildStore().load(f"{DEFAULT_EXTENDED_IMAGE_NAME}:forge-ubuntu-marker")
    assert extended_record is not None
    assert_base_layer_present(extended_record.base_image, extended_record.image_ref)


def test_local_custom_extension_rebuilds_on_base_layer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    require_integration()
    workspace, env = _setup_extension_workspace(monkeypatch, tmp_path)
    exit_code, output = _run_extension_check(env, workspace)
    assert exit_code == 0, output

    extended_store = ExtendedBuildStore()
    record = extended_store.load(f"{DEFAULT_EXTENDED_IMAGE_NAME}:forge-ubuntu-marker")
    assert record is not None

    replace_final_image(record.image_ref, tmp_path)

    exit_code, output = _run_extension_check(env, workspace)
    assert exit_code == 0, output
    assert_base_layer_present(record.base_image, record.image_ref)


def _setup_extension_workspace(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> tuple[Path, dict[str, str]]:
    workspace, env = setup_workspace(
        monkeypatch,
        tmp_path,
        "forge",
        docker_args="--entrypoint=/bin/sh",
    )
    agent_dir = custom_agents_dir() / "forge"
    copy_forge_sample(agent_dir)

    extension_dir = custom_extensions_dir() / "marker"
    extension_dir.parent.mkdir(parents=True, exist_ok=True)
    copy_marker_extension_sample(extension_dir)

    store = SettingsStore()
    project_cfg = store.load_project(workspace)
    project_cfg.agents["forge"] = AgentConfig(
        base="ubuntu",
        docker_args="--entrypoint=/bin/sh",
        image_ref=f"{DEFAULT_EXTENDED_IMAGE_NAME}:forge-ubuntu-marker",
        extensions=["marker"],
    )
    store.save_project(workspace, project_cfg)
    return workspace, env


def _run_extension_check(env: dict[str, str], workspace: Path) -> tuple[int, str]:
    return run_cli_pty(
        ["forge", "-c", "test -f /usr/local/share/aicage-extensions/marker.txt"],
        env=env,
        cwd=workspace,
    )
