from pathlib import Path

import pytest

from aicage.registry.local_build._store import BuildStore

from .._helpers import force_record_agent_version, require_integration, run_agent_version, setup_workspace

pytestmark = pytest.mark.integration


def test_local_builtin_agent_rebuilds(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    require_integration()
    workspace, env = setup_workspace(monkeypatch, tmp_path, "claude")
    run_agent_version(env, workspace, "claude")

    store = BuildStore()
    record = store.load("claude", "ubuntu")
    assert record is not None

    force_record_agent_version(
        store,
        record,
        agent_version="0.0.0",
    )
    run_agent_version(env, workspace, "claude")
    updated = store.load("claude", "ubuntu")
    assert updated is not None
    assert updated.agent_version != "0.0.0"
