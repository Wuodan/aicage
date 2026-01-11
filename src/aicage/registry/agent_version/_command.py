from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from aicage._logging import get_logger
from aicage.docker.run import run_builder_version_check


@dataclass(frozen=True)
class _CommandResult:
    success: bool
    output: str
    error: str


def run_version_check_image(image_ref: str, definition_dir: Path) -> _CommandResult:
    process = run_builder_version_check(image_ref, definition_dir)
    return _from_process(process, "version check image")


def run_host(script_path: Path) -> _CommandResult:
    if not os.access(script_path, os.X_OK):
        get_logger().warning(
            "version.sh at %s is not executable; running with /bin/bash.",
            script_path,
        )
    return _run_command(["/bin/bash", str(script_path)], "host")


def _run_command(command: list[str], context: str) -> _CommandResult:
    process = subprocess.run(command, check=False, capture_output=True, text=True)
    return _from_process(process, context)


def _from_process(process: subprocess.CompletedProcess[str], context: str) -> _CommandResult:
    output = process.stdout.strip() if process.stdout else ""
    if process.returncode == 0 and output:
        return _CommandResult(success=True, output=output, error="")

    stderr = process.stderr.strip() if process.stderr else ""
    error = stderr or output or f"Version check failed in {context}."
    return _CommandResult(success=False, output=output, error=error)
