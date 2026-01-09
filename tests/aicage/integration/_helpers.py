import os
import pty
import select
import stat
import subprocess
import sys
from pathlib import Path
from shutil import copytree

import pytest

from aicage.config.config_store import SettingsStore
from aicage.config.project_config import AgentConfig, ProjectConfig
from aicage.docker.query import get_local_rootfs_layers
from aicage.paths import DEFAULT_CUSTOM_AGENTS_DIR, DEFAULT_CUSTOM_EXTENSIONS_DIR
from aicage.registry.local_build._store import BuildRecord, BuildStore


def run_cli_pty(args: list[str], env: dict[str, str], cwd: Path) -> tuple[int, str]:
    master_fd, slave_fd = pty.openpty()
    process = subprocess.Popen(
        [sys.executable, "-m", "aicage", *args],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        cwd=cwd,
        env=env,
        close_fds=True,
    )
    os.close(slave_fd)

    chunks: list[bytes] = []
    while True:
        read_ready, _, _ = select.select([master_fd], [], [], 0.2)
        if master_fd in read_ready:
            try:
                data = os.read(master_fd, 4096)
            except OSError:
                data = b""
            if data:
                chunks.append(data)
            elif process.poll() is not None:
                break
        elif process.poll() is not None:
            break

    process.wait()
    os.close(master_fd)
    output = b"".join(chunks).decode(errors="replace")
    return process.returncode, output


def require_integration() -> None:
    if not os.environ.get("AICAGE_RUN_INTEGRATION"):
        pytest.skip("Set AICAGE_RUN_INTEGRATION=1 to run integration tests.")


def setup_workspace(
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

    store = SettingsStore()
    agent_cfg = AgentConfig(base="ubuntu")
    if docker_args:
        agent_cfg.docker_args = docker_args
    project_cfg = ProjectConfig(
        path=str(workspace),
        agents={agent_name: agent_cfg},
    )
    store.save_project(workspace, project_cfg)

    return workspace, build_cli_env(home_dir)


def run_agent_version(env: dict[str, str], workspace: Path, agent_name: str) -> None:
    exit_code, output = run_cli_pty([agent_name, "--version"], env=env, cwd=workspace)
    assert exit_code == 0, output
    output_lines = [line.strip() for line in output.splitlines() if line.strip()]
    assert output_lines
    assert output_lines[-1]


def force_record_agent_version(
    store: BuildStore,
    record: BuildRecord,
    *,
    agent_version: str,
) -> None:
    updated = BuildRecord(
        agent=record.agent,
        base=record.base,
        agent_version=agent_version,
        base_image=record.base_image,
        image_ref=record.image_ref,
        built_at=record.built_at,
    )
    store.save(updated)


def replace_final_image(image_ref: str, tmp_path: Path) -> None:
    build_dir = tmp_path / "override"
    build_dir.mkdir(exist_ok=True)
    dockerfile = build_dir / "Dockerfile"
    dockerfile.write_text("FROM alpine:latest\nRUN echo replaced\n", encoding="utf-8")
    subprocess.run(
        [
            "docker",
            "build",
            "--no-cache",
            "--pull",
            "--tag",
            image_ref,
            str(build_dir),
        ],
        check=True,
        capture_output=True,
    )


def build_dummy_image(image_ref: str, tmp_path: Path) -> str:
    context_dir = tmp_path / "dummy-image"
    context_dir.mkdir(parents=True, exist_ok=True)
    (context_dir / "Dockerfile").write_text(
        "\n".join(
            [
                "FROM alpine:latest",
                "RUN echo dummy > /dummy",
                "CMD [\"/bin/bash\", \"-c\", \"echo dummy\"]",
            ]
        ),
        encoding="utf-8",
    )
    subprocess.run(
        ["docker", "build", "-t", image_ref, str(context_dir)],
        check=True,
        capture_output=True,
    )
    result = subprocess.run(
        ["docker", "image", "inspect", "-f", "{{.Id}}", image_ref],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def assert_base_layer_present(base_image_ref: str, final_image_ref: str) -> None:
    base_layers = get_local_rootfs_layers(base_image_ref)
    assert base_layers is not None
    final_layers = get_local_rootfs_layers(final_image_ref)
    assert final_layers is not None
    assert base_layers[-1] in final_layers


def build_cli_env(home_dir: Path) -> dict[str, str]:
    env = dict(os.environ)
    env["HOME"] = str(home_dir)
    repo_root = Path(__file__).resolve().parents[3]
    env["PYTHONPATH"] = str(repo_root / "src")
    for key in list(env):
        if key == "AGENT" or key.startswith("AICAGE_"):
            env.pop(key, None)
    return env


def custom_agents_dir() -> Path:
    return DEFAULT_CUSTOM_AGENTS_DIR.expanduser()


def copy_forge_sample(target_dir: Path) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    source_dir = repo_root / "doc/sample/custom/agents/forge"
    copytree(source_dir, target_dir, dirs_exist_ok=True)
    _make_executable(target_dir / "install.sh")
    _make_executable(target_dir / "version.sh")


def custom_extensions_dir() -> Path:
    return DEFAULT_CUSTOM_EXTENSIONS_DIR.expanduser()


def copy_marker_extension_sample(target_dir: Path) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    source_dir = repo_root / "doc/sample/custom/extensions/marker"
    copytree(source_dir, target_dir, dirs_exist_ok=True)
    for script in (target_dir / "scripts").glob("*.sh"):
        _make_executable(script)


def _make_executable(path: Path) -> None:
    current = path.stat().st_mode
    path.chmod(current | stat.S_IEXEC)
