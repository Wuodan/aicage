import subprocess
from pathlib import Path

import pytest

from aicage.config.custom_base.loader import load_custom_bases
from aicage.config.images_metadata.loader import load_images_metadata
from aicage.constants import IMAGE_REGISTRY, IMAGE_REPOSITORY
from aicage.docker.query import get_local_repo_digest_for_repo

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


def test_builtin_agent_pulls_newer_digest(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    require_integration()
    docker_args = "--entrypoint=/bin/bash"
    workspace, env = setup_workspace(monkeypatch, tmp_path, "copilot", docker_args=docker_args)
    images_metadata = load_images_metadata(load_custom_bases())
    image_ref = images_metadata.agents["copilot"].valid_bases["ubuntu"]
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
