from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from aicage._logging import get_logger
from aicage.errors import CliError


def run_pull(image_ref: str, log_path: Path) -> None:
    logger = get_logger()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[aicage] Pulling image {image_ref} (logs: {log_path})...")
    logger.info("Pulling image %s (logs: %s)", image_ref, log_path)

    last_nonempty_line = ""
    pull_process = subprocess.Popen(
        ["docker", "pull", image_ref],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    with log_path.open("w", encoding="utf-8") as log_handle:
        if pull_process.stdout is not None:
            for line in pull_process.stdout:
                log_handle.write(line)
                log_handle.flush()
                stripped = line.strip()
                if stripped:
                    last_nonempty_line = stripped

    pull_process.wait()

    if pull_process.returncode == 0:
        logger.info("Image pull succeeded for %s", image_ref)
        return

    inspect = subprocess.run(
        ["docker", "image", "inspect", image_ref],
        check=False,
        capture_output=True,
        text=True,
    )
    if inspect.returncode == 0:
        msg = last_nonempty_line or f"docker pull failed for {image_ref}"
        print(f"[aicage] Warning: {msg}. Using local image.", file=sys.stderr)
        logger.warning("Pull failed for %s, using local image: %s", image_ref, msg)
        return

    detail = last_nonempty_line or f"docker pull failed for {image_ref}"
    logger.error("Pull failed for %s: %s", image_ref, detail)
    raise CliError(detail)
