from __future__ import annotations

import json
from pathlib import Path

from aicage._logging import get_logger
from aicage.docker._client import get_docker_client


def run_pull(image_ref: str, log_path: Path) -> None:
    logger = get_logger()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[aicage] Pulling image {image_ref} (logs: {log_path})...")
    logger.info("Pulling image %s (logs: %s)", image_ref, log_path)

    client = get_docker_client()
    with log_path.open("w", encoding="utf-8") as log_handle:
        for event in client.api.pull(image_ref, stream=True, decode=True):
            log_handle.write(f"{_format_pull_event(event)}\n")
            log_handle.flush()

    logger.info("Image pull succeeded for %s", image_ref)


def _format_pull_event(event: object) -> str:
    if isinstance(event, bytes):
        return event.decode("utf-8", errors="replace").rstrip("\n")
    if isinstance(event, str):
        return event.rstrip("\n")
    if isinstance(event, dict):
        return json.dumps(event, ensure_ascii=True)
    return str(event).rstrip("\n")
