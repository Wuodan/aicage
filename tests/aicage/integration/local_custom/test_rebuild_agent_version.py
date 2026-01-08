import os
from pathlib import Path

import pytest

from aicage.registry.custom_agent.loader import DEFAULT_CUSTOM_AGENTS_DIR
from aicage.registry.local_build._store import BuildStore

from .._helpers import (
    copy_forge_sample,
    force_record_agent_version,
    require_integration,
    run_agent_version,
    setup_workspace,
)

pytestmark = pytest.mark.integration


def test_custom_agent_rebuilds(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    require_integration()
    workspace, env = setup_workspace(monkeypatch, tmp_path, "forge")
    agent_dir = Path(os.path.expanduser(DEFAULT_CUSTOM_AGENTS_DIR)) / "forge"
    copy_forge_sample(agent_dir)

    run_agent_version(env, workspace, "forge")
    store = BuildStore()
    record = store.load("forge", "ubuntu")
    assert record is not None

    force_record_agent_version(
        store,
        record,
        agent_version="0.0.0",
    )
    run_agent_version(env, workspace, "forge")
    updated = store.load("forge", "ubuntu")
    assert updated is not None
    assert updated.agent_version != "0.0.0"
