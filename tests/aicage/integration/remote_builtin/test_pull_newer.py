import subprocess
from pathlib import Path
from unittest import mock

import pytest

from aicage.config.agent.loader import load_agents
from aicage.config.base.loader import load_bases
from aicage.constants import IMAGE_REGISTRY, IMAGE_REPOSITORY
from aicage.docker.query import get_local_repo_digest_for_repo
from aicage.registry import _image_pull as image_pull

from .._helpers import build_dummy_image, require_integration, run_cli_pty, setup_workspace

pytestmark = pytest.mark.integration

def _image_id(image_ref: str) -> str:
    result = subprocess.run(
        ["docker", "image", "inspect", "-f", "{{.Id}}", image_ref],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _repo_digest_pairs() -> set[tuple[str, str]]:
    expected_parts = 2
    result = subprocess.run(
        ["docker", "image", "ls", "--digests", "--format", "{{.Repository}} {{.Digest}}"],
        check=True,
        capture_output=True,
        text=True,
    )
    pairs: set[tuple[str, str]] = set()
    for line in result.stdout.splitlines():
        parts = [part for part in line.strip().split(" ", 1) if part]
        if len(parts) != expected_parts:
            continue
        repository, digest = parts
        if repository == "<none>" or digest == "<none>":
            continue
        pairs.add((repository, digest))
    return pairs


def test_builtin_agent_pulls_newer_digest(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    require_integration()
    docker_args = "--entrypoint=/bin/bash"
    workspace, env = setup_workspace(monkeypatch, tmp_path, "copilot", docker_args=docker_args)
    bases = load_bases()
    agents = load_agents(bases)
    image_ref = agents["copilot"].valid_bases["ubuntu"]
    local_id_before = build_dummy_image(image_ref, tmp_path)
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

        repository = f"{IMAGE_REGISTRY}/{IMAGE_REPOSITORY}"
        local_digest = get_local_repo_digest_for_repo(image_ref, repository)
        assert local_digest is not None
    finally:
        subprocess.run(["docker", "image", "rm", "-f", image_ref], check=False, capture_output=True)


def test_builtin_agent_cleans_old_digest_after_pull(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    require_integration()
    docker_args = "--entrypoint=/bin/bash"
    workspace, env = setup_workspace(monkeypatch, tmp_path, "copilot", docker_args=docker_args)
    bases = load_bases()
    agents = load_agents(bases)
    image_ref = agents["copilot"].valid_bases["ubuntu"]
    subprocess.run(["docker", "pull", image_ref], check=True, capture_output=True)
    repository = f"{IMAGE_REGISTRY}/{IMAGE_REPOSITORY}"
    old_digest = get_local_repo_digest_for_repo(image_ref, repository)
    assert old_digest is not None
    subprocess.run(
        ["docker", "pull", f"{repository}@{old_digest}"],
        check=True,
        capture_output=True,
    )
    before_pairs = _repo_digest_pairs()
    assert (repository, old_digest) in before_pairs
    build_dummy_image(image_ref, tmp_path)
    try:
        with (
            mock.patch(
                "aicage.registry._pull_decision.get_local_repo_digest",
                return_value=old_digest,
            ),
            mock.patch(
                "aicage.registry._pull_decision.get_remote_digest",
                return_value="sha256:new",
            ),
            mock.patch(
                "aicage.registry._image_pull.resolve_verified_digest",
                return_value=f"{repository}@sha256:new",
            ),
            mock.patch(
                "aicage.registry._image_pull.run_pull",
                return_value=None,
            ),
            mock.patch(
                "aicage.registry._image_pull.get_local_repo_digest_for_repo",
                return_value=old_digest,
            ),
            mock.patch(
                "aicage.docker.query.get_local_repo_digest_for_repo",
                return_value="sha256:new",
            ),
        ):
            image_pull.pull_image(image_ref)
        after_pairs = _repo_digest_pairs()
        assert (repository, old_digest) not in after_pairs
    finally:
        subprocess.run(["docker", "image", "rm", "-f", image_ref], check=False, capture_output=True)
