from __future__ import annotations

from dataclasses import dataclass

from aicage.config.runtime_config import RunConfig
from aicage.docker.query import get_local_repo_digest
from aicage.docker.remote_query import get_remote_repo_digest
from aicage.docker.types import ImageRefRepository, RegistryApiConfig, RemoteImageRef


@dataclass(frozen=True)
class _PullDecision:
    should_pull: bool


def decide_pull(run_config: RunConfig) -> _PullDecision:
    local_digest = get_local_repo_digest(
        ImageRefRepository(
            image_ref=run_config.image_ref,
            repository=f"{run_config.global_cfg.image_registry}/{run_config.global_cfg.image_repository}",
        )
    )
    if local_digest is None:
        return _PullDecision(should_pull=True)

    remote_digest = get_remote_repo_digest(
        RemoteImageRef(
            image=ImageRefRepository(
                image_ref=run_config.image_ref,
                repository=run_config.global_cfg.image_repository,
            ),
            registry_api=RegistryApiConfig(
                registry_api_url=run_config.global_cfg.image_registry_api_url,
                registry_api_token_url=run_config.global_cfg.image_registry_api_token_url,
            ),
        )
    )
    if remote_digest is None:
        return _PullDecision(should_pull=False)

    return _PullDecision(should_pull=local_digest != remote_digest)
