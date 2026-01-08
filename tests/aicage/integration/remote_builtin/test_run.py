from pathlib import Path

import pytest

from .._helpers import require_integration, run_agent_version, setup_workspace

pytestmark = pytest.mark.integration


def test_builtin_agent_runs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    require_integration()
    workspace, env = setup_workspace(monkeypatch, tmp_path, "codex")
    run_agent_version(env, workspace, "codex")
