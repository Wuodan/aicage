from pathlib import Path

import pytest

from ._helpers import build_cli_env, require_integration, run_cli_pty

pytestmark = pytest.mark.integration


def test_refuses_to_start_when_cwd_is_home(tmp_path: Path) -> None:
    require_integration()
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    env = build_cli_env(home_dir)

    exit_code, output = run_cli_pty(
        ["codex", "--version"],
        env=env,
        cwd=home_dir,
        input_data="\n\n",
    )

    assert exit_code == 1
    assert "Refusing to start: this would mount your home directory into the container." in output
