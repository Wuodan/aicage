from pathlib import Path

import pytest

from aicage.config.config_store import SettingsStore
from aicage.constants import DEFAULT_EXTENDED_IMAGE_NAME

from .._helpers import (
    copy_custom_base_sample,
    copy_forge_sample,
    copy_marker_extension_sample,
    custom_agents_dir,
    custom_bases_dir,
    custom_extensions_dir,
    require_integration,
    run_cli_pty,
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
def test_custom_base_extension_builds_and_runs(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    agent_name: str,
    is_custom_agent: bool,
) -> None:
    require_integration()
    workspace, env = setup_workspace(
        monkeypatch,
        tmp_path,
        agent_name,
        docker_args="--entrypoint=/bin/sh",
    )
    base_dir = custom_bases_dir() / _CUSTOM_BASE_NAME
    base_dir.parent.mkdir(parents=True, exist_ok=True)
    copy_custom_base_sample(_CUSTOM_BASE_NAME, base_dir)
    if is_custom_agent:
        agent_dir = custom_agents_dir() / agent_name
        copy_forge_sample(agent_dir)

    extension_dir = custom_extensions_dir() / "marker"
    extension_dir.parent.mkdir(parents=True, exist_ok=True)
    copy_marker_extension_sample(extension_dir)

    _configure_extension(workspace, agent_name, _CUSTOM_BASE_NAME)

    exit_code, output = run_cli_pty(
        [agent_name, "-c", "test -f /usr/local/share/aicage-extensions/marker.txt"],
        env=env,
        cwd=workspace,
    )
    assert exit_code == 0, output


def _configure_extension(workspace: Path, agent_name: str, base_name: str) -> None:
    store = SettingsStore()
    project_cfg = store.load_project(workspace)
    agent_cfg = project_cfg.agents[agent_name]
    agent_cfg.base = base_name
    agent_cfg.docker_args = "--entrypoint=/bin/sh"
    agent_cfg.image_ref = f"{DEFAULT_EXTENDED_IMAGE_NAME}:{agent_name}-{base_name}-marker"
    agent_cfg.extensions = ["marker"]
    store.save_project(workspace, project_cfg)
