from aicage._logging import get_logger
from aicage.constants import IMAGE_REGISTRY, IMAGE_REPOSITORY
from aicage.docker.pull import run_pull
from aicage.docker.query import cleanup_old_digest, get_local_repo_digest_for_repo
from aicage.registry._logs import pull_log_path
from aicage.registry._pull_decision import decide_pull
from aicage.registry._signature import resolve_verified_digest


def pull_image(image_ref: str) -> None:
    logger = get_logger()
    repository = f"{IMAGE_REGISTRY}/{IMAGE_REPOSITORY}"
    local_digest = get_local_repo_digest_for_repo(image_ref, repository)
    should_pull = decide_pull(image_ref)
    if not should_pull:
        logger.info("Image pull not required for %s", image_ref)
        return

    resolve_verified_digest(image_ref)
    log_path = pull_log_path(image_ref)
    run_pull(image_ref, log_path)
    cleanup_old_digest(repository, local_digest, image_ref)
