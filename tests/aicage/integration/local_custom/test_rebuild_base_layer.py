from pathlib import Path

import pytest

from aicage.registry.local_build._store import BuildStore

from .._helpers import (
    assert_base_layer_present,
    copy_forge_sample,
    custom_agents_dir,
    replace_final_image,
    require_integration,
    run_agent_version,
    setup_workspace,
)

pytestmark = pytest.mark.integration


def test_custom_agent_rebuilds_on_base_layer(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    require_integration()
    workspace, env = setup_workspace(monkeypatch, tmp_path, "forge")
    agent_dir = custom_agents_dir() / "forge"
    copy_forge_sample(agent_dir)

    run_agent_version(env, workspace, "forge")
    store = BuildStore()
    record = store.load("forge", "ubuntu")
    assert record is not None

    replace_final_image(record.image_ref, tmp_path)
    run_agent_version(env, workspace, "forge")
    updated = store.load("forge", "ubuntu")
    assert updated is not None
    assert_base_layer_present(record.base_image, record.image_ref)
