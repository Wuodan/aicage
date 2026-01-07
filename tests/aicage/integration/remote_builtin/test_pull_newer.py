import os
import subprocess
from pathlib import Path

import pytest

from aicage.config.config_store import SettingsStore
from aicage.config.project_config import AgentConfig, ProjectConfig
from aicage.registry import _local_query
from aicage.registry.images_metadata.loader import load_images_metadata

from .._helpers import build_cli_env, run_cli_pty

pytestmark = pytest.mark.integration


def _require_integration() -> None:
    if not os.environ.get("AICAGE_RUN_INTEGRATION"):
        pytest.skip("Set AICAGE_RUN_INTEGRATION=1 to run integration tests.")


def _write_project_config(workspace: Path, agent_name: str, *, docker_args: str | None = None) -> None:
    store = SettingsStore()
    agent_cfg = AgentConfig(base="ubuntu")
    if docker_args:
        agent_cfg.docker_args = docker_args
    project_cfg = ProjectConfig(
        path=str(workspace),
        agents={agent_name: agent_cfg},
    )
    store.save_project(workspace, project_cfg)


def _setup_workspace(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    agent_name: str,
    *,
    docker_args: str | None = None,
) -> tuple[Path, dict[str, str]]:
    home_dir = tmp_path / "home"
    workspace = tmp_path / "workspace"
    home_dir.mkdir()
    workspace.mkdir()
    monkeypatch.setenv("HOME", str(home_dir))
    monkeypatch.chdir(workspace)
    _write_project_config(workspace, agent_name, docker_args=docker_args)
    env = build_cli_env(home_dir)
    return workspace, env


def _image_id(image_ref: str) -> str:
    result = subprocess.run(
        ["docker", "image", "inspect", "-f", "{{.Id}}", image_ref],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _build_dummy_image(image_ref: str, tmp_path: Path) -> str:
    context_dir = tmp_path / "dummy-image"
    context_dir.mkdir(parents=True, exist_ok=True)
    (context_dir / "Dockerfile").write_text(
        "\n".join(
            [
                "FROM alpine:latest",
                "RUN echo dummy > /dummy",
                "CMD [\"/bin/sh\", \"-c\", \"echo dummy\"]",
            ]
        ),
        encoding="utf-8",
    )
    subprocess.run(
        ["docker", "build", "-t", image_ref, str(context_dir)],
        check=True,
        capture_output=True,
    )
    return _image_id(image_ref)


def test_builtin_agent_pulls_newer_digest(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _require_integration()
    docker_args = "--entrypoint=/bin/sh"
    workspace, env = _setup_workspace(monkeypatch, tmp_path, "copilot", docker_args=docker_args)
    store = SettingsStore()
    global_cfg = store.load_global()
    images_metadata = load_images_metadata(global_cfg.local_image_repository)
    image_ref = images_metadata.agents["copilot"].valid_bases["ubuntu"]
    local_id_before = _build_dummy_image(image_ref, tmp_path)
    try:
        exit_code, output = run_cli_pty(
            ["copilot", "-c", "echo ok"],
            env=env,
            cwd=workspace,
        )
        assert exit_code == 0, output
        output_lines = [line.strip() for line in output.splitlines() if line.strip()]
        assert output_lines
        assert output_lines[-1]
        local_id_after = _image_id(image_ref)
        assert local_id_after != local_id_before

        repository = f"{global_cfg.image_registry}/{global_cfg.image_repository}"
        local_digest = _local_query.get_local_repo_digest_for_repo(image_ref, repository)
        assert local_digest is not None
    finally:
        subprocess.run(["docker", "image", "rm", "-f", image_ref], check=False, capture_output=True)
