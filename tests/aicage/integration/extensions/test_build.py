from pathlib import Path

import pytest

from aicage.config.config_store import SettingsStore
from aicage.config.project_config import AgentConfig

from .._helpers import (
    copy_marker_extension_sample,
    custom_extensions_dir,
    require_integration,
    run_cli_pty,
    setup_workspace,
)

pytestmark = pytest.mark.integration


def test_extension_builds_and_runs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    require_integration()
    workspace, env = setup_workspace(
        monkeypatch,
        tmp_path,
        "codex",
        docker_args="--entrypoint=/bin/sh",
    )

    extension_dir = custom_extensions_dir() / "marker"
    extension_dir.parent.mkdir(parents=True, exist_ok=True)
    copy_marker_extension_sample(extension_dir)

    store = SettingsStore()
    project_cfg = store.load_project(workspace)
    project_cfg.agents["codex"] = AgentConfig(
        base="ubuntu",
        docker_args="--entrypoint=/bin/sh",
        image_ref="aicage-extended:codex-ubuntu-marker",
        extensions=["marker"],
    )
    store.save_project(workspace, project_cfg)

    exit_code, output = run_cli_pty(
        ["codex", "-c", "test -f /usr/local/share/aicage-extensions/marker.txt"],
        env=env,
        cwd=workspace,
    )
    assert exit_code == 0, output
