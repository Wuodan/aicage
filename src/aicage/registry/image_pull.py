from __future__ import annotations

from aicage._logging import get_logger
from aicage.config.global_config import GlobalConfig
from aicage.docker.pull import run_pull
from aicage.registry._logs import pull_log_path
from aicage.registry._pull_decision import decide_pull


def pull_image(image_ref: str, global_cfg: GlobalConfig) -> None:
    logger = get_logger()
    decision = decide_pull(image_ref, global_cfg)
    if not decision.should_pull:
        logger.info("Image pull not required for %s", image_ref)
        return

    log_path = pull_log_path(image_ref)
    run_pull(image_ref, log_path)
