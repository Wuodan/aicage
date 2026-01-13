import subprocess
from pathlib import Path

import pytest

from aicage.config.config_store import SettingsStore
from aicage.constants import DEFAULT_EXTENDED_IMAGE_NAME
from aicage.registry.extension_build._extended_store import ExtendedBuildStore

from .._helpers import (
    assert_base_layer_present,
    build_dummy_image,
    copy_marker_extension_sample,
    custom_extensions_dir,
    require_integration,
    run_cli_pty,
    setup_workspace,
)

pytestmark = pytest.mark.integration


def _image_id(image_ref: str) -> str:
    result = subprocess.run(
        ["docker", "image", "inspect", "-f", "{{.Id}}", image_ref],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def test_remote_builtin_extension_rebuilds_on_base_change(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
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
    agent_cfg = project_cfg.agents["codex"]
    agent_cfg.base = "ubuntu"
    agent_cfg.docker_args = "--entrypoint=/bin/sh"
    agent_cfg.image_ref = f"{DEFAULT_EXTENDED_IMAGE_NAME}:codex-ubuntu-marker"
    agent_cfg.extensions = ["marker"]
    store.save_project(workspace, project_cfg)

    exit_code, output = run_cli_pty(
        ["codex", "-c", "test -f /usr/local/share/aicage-extensions/marker.txt"],
        env=env,
        cwd=workspace,
    )
    assert exit_code == 0, output

    extended_store = ExtendedBuildStore()
    record = extended_store.load(f"{DEFAULT_EXTENDED_IMAGE_NAME}:codex-ubuntu-marker")
    assert record is not None

    dummy_id = build_dummy_image(record.base_image, tmp_path)

    exit_code, output = run_cli_pty(
        ["codex", "-c", "test -f /usr/local/share/aicage-extensions/marker.txt"],
        env=env,
        cwd=workspace,
    )
    assert exit_code == 0, output

    local_id_after = _image_id(record.base_image)
    assert local_id_after != dummy_id
    assert_base_layer_present(record.base_image, record.image_ref)
