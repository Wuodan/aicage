from pathlib import Path

import pytest

from aicage import paths as paths_module
from aicage.registry.local_build._store import BuildStore

from .._helpers import (
    copy_forge_sample,
    custom_agents_dir,
    require_integration,
    run_agent_version,
    setup_workspace,
)

pytestmark = pytest.mark.integration


def test_custom_agent_build_and_version(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    require_integration()
    monkeypatch.setattr(
        paths_module,
        "IMAGE_BUILD_STATE_DIR",
        tmp_path / "state" / "image" / "build",
    )
    workspace, env = setup_workspace(monkeypatch, tmp_path, "forge")
    agent_dir = custom_agents_dir() / "forge"
    copy_forge_sample(agent_dir)

    run_agent_version(env, workspace, "forge")

    record = BuildStore().load("forge", "ubuntu")
    assert record is not None
