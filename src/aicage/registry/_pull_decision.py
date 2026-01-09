from __future__ import annotations

from dataclasses import dataclass

from aicage.config.runtime_config import RunConfig
from aicage.docker.query import get_local_repo_digest
from aicage.docker.remote_query import get_remote_repo_digest_for_repo


@dataclass(frozen=True)
class _PullDecision:
    should_pull: bool


def decide_pull(run_config: RunConfig) -> _PullDecision:
    local_digest = get_local_repo_digest(run_config)
    if local_digest is None:
        return _PullDecision(should_pull=True)

    remote_digest = get_remote_repo_digest_for_repo(
        run_config.image_ref,
        run_config.global_cfg.image_repository,
        run_config.global_cfg,
    )
    if remote_digest is None:
        return _PullDecision(should_pull=False)

    return _PullDecision(should_pull=local_digest != remote_digest)
