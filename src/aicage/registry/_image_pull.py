from __future__ import annotations

from aicage._logging import get_logger
from aicage.docker.pull import run_pull
from aicage.registry._logs import pull_log_path
from aicage.registry._pull_decision import decide_pull


def pull_image(image_ref: str) -> None:
    logger = get_logger()
    should_pull = decide_pull(image_ref)
    if not should_pull:
        logger.info("Image pull not required for %s", image_ref)
        return

    log_path = pull_log_path(image_ref)
    run_pull(image_ref, log_path)
