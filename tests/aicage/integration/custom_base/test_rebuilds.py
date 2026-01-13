from pathlib import Path

import pytest
import yaml

from aicage.config.config_store import SettingsStore
from aicage.registry.local_build._custom_base_store import CustomBaseBuildStore
from aicage.registry.local_build._store import BuildStore

from .._helpers import (
    assert_base_layer_present,
    copy_custom_base_sample,
    custom_bases_dir,
    force_record_agent_version,
    require_integration,
    run_agent_version,
    setup_workspace,
)

pytestmark = pytest.mark.integration


def test_custom_base_rebuilds_on_agent_version(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    require_integration()
    base_name = "php"
    workspace, env = setup_workspace(monkeypatch, tmp_path, "codex")
    base_dir = custom_bases_dir() / base_name
    base_dir.parent.mkdir(parents=True, exist_ok=True)
    copy_custom_base_sample(base_name, base_dir)
    _set_agent_base(workspace, "codex", base_name)

    run_agent_version(env, workspace, "codex")
    store = BuildStore()
    record = store.load("codex", base_name)
    assert record is not None

    force_record_agent_version(store, record, agent_version="0.0.0")
    run_agent_version(env, workspace, "codex")
    updated = store.load("codex", base_name)
    assert updated is not None
    assert updated.agent_version != "0.0.0"


def test_custom_base_rebuilds_on_digest_change_ghcr(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    require_integration()
    base_name = "debian-mirror"
    workspace, env = setup_workspace(monkeypatch, tmp_path, "codex")
    base_dir = custom_bases_dir() / base_name
    base_dir.parent.mkdir(parents=True, exist_ok=True)
    copy_custom_base_sample(base_name, base_dir)
    _update_from_image(base_dir, "ghcr.io/rblaine95/debian:bookworm")
    _set_agent_base(workspace, "codex", base_name)

    run_agent_version(env, workspace, "codex")
    base_store = CustomBaseBuildStore()
    record = base_store.load(base_name)
    assert record is not None
    assert record.from_image == "ghcr.io/rblaine95/debian:bookworm"
    assert record.from_image_digest

    _update_from_image(base_dir, "ghcr.io/rblaine95/debian:bookworm-slim")
    run_agent_version(env, workspace, "codex")
    updated = base_store.load(base_name)
    assert updated is not None
    assert updated.from_image == "ghcr.io/rblaine95/debian:bookworm-slim"
    assert updated.from_image_digest
    assert updated.from_image_digest != record.from_image_digest

    build_record = BuildStore().load("codex", base_name)
    assert build_record is not None
    assert_base_layer_present(updated.image_ref, build_record.image_ref)


def test_custom_base_rebuilds_on_digest_change_docker(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    require_integration()
    base_name = "php"
    workspace, env = setup_workspace(monkeypatch, tmp_path, "codex")
    base_dir = custom_bases_dir() / base_name
    base_dir.parent.mkdir(parents=True, exist_ok=True)
    copy_custom_base_sample(base_name, base_dir)
    _update_from_image(base_dir, "php:8.2")
    _set_agent_base(workspace, "codex", base_name)

    run_agent_version(env, workspace, "codex")
    base_store = CustomBaseBuildStore()
    record = base_store.load(base_name)
    assert record is not None
    assert record.from_image == "php:8.2"
    assert record.from_image_digest

    _update_from_image(base_dir, "php:8.3")
    run_agent_version(env, workspace, "codex")
    updated = base_store.load(base_name)
    assert updated is not None
    assert updated.from_image == "php:8.3"
    assert updated.from_image_digest
    assert updated.from_image_digest != record.from_image_digest

    build_record = BuildStore().load("codex", base_name)
    assert build_record is not None
    assert_base_layer_present(updated.image_ref, build_record.image_ref)


def _set_agent_base(workspace: Path, agent_name: str, base_name: str) -> None:
    store = SettingsStore()
    project_cfg = store.load_project(workspace)
    agent_cfg = project_cfg.agents[agent_name]
    agent_cfg.base = base_name
    store.save_project(workspace, project_cfg)


def _update_from_image(base_dir: Path, from_image: str) -> None:
    definition_path = _find_base_definition(base_dir)
    payload = yaml.safe_load(definition_path.read_text(encoding="utf-8")) or {}
    payload["from_image"] = from_image
    definition_path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")


def _find_base_definition(base_dir: Path) -> Path:
    for filename in ("base.yml", "base.yaml"):
        candidate = base_dir / filename
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"Custom base at '{base_dir}' is missing base.yml.")
