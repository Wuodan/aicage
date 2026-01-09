from __future__ import annotations

from aicage._logging import get_logger
from aicage.config.runtime_config import RunConfig
from aicage.docker.pull import run_pull
from aicage.registry._logs import pull_log_path
from aicage.registry._pull_decision import decide_pull


def pull_image(run_config: RunConfig) -> None:
    logger = get_logger()
    decision = decide_pull(run_config)
    if not decision.should_pull:
        logger.info("Image pull not required for %s", run_config.image_ref)
        return

    log_path = pull_log_path(run_config.image_ref)
    run_pull(run_config.image_ref, log_path)
