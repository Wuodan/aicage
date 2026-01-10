from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from logging import Logger
from pathlib import Path

from aicage._logging import get_logger
from aicage.config.global_config import GlobalConfig
from aicage.config.images_metadata.models import AgentMetadata
from aicage.docker.pull import run_pull
from aicage.docker.query import get_local_repo_digest
from aicage.docker.remote_query import get_remote_repo_digest
from aicage.docker.run import run_builder_version_check
from aicage.docker.types import ImageRefRepository, RegistryApiConfig, RemoteImageRef
from aicage.registry._logs import pull_log_path
from aicage.registry.errors import RegistryError

from .store import VersionCheckStore


class AgentVersionChecker:
    def __init__(self, global_cfg: GlobalConfig, store: VersionCheckStore | None = None) -> None:
        self._global_cfg = global_cfg
        self._store = store or VersionCheckStore()

    def get_version(
        self,
        agent_name: str,
        _agent_metadata: AgentMetadata,
        definition_dir: Path,
    ) -> str:
        logger = get_logger()
        script_path = definition_dir / "version.sh"
        if not script_path.is_file():
            raise RegistryError(f"Agent '{agent_name}' is missing version.sh at {script_path}.")

        errors: list[str] = []
        host_result = _run_host(script_path)
        if host_result.success:
            logger.info("Version check succeeded on host for %s", agent_name)
            self._store.save(agent_name, host_result.output)
            return host_result.output

        logger.warning(
            "Version check failed on host for %s: %s",
            agent_name,
            host_result.error,
        )
        errors.append(host_result.error)

        builder_result = _run_builder(
            image_ref=self._global_cfg.version_check_image,
            definition_dir=definition_dir,
            global_cfg=self._global_cfg,
        )
        if builder_result.success:
            logger.info("Version check succeeded in builder for %s", agent_name)
            self._store.save(agent_name, builder_result.output)
            return builder_result.output

        logger.warning(
            "Version check failed in builder for %s: %s",
            agent_name,
            builder_result.error,
        )
        errors.append(builder_result.error)
        logger.error("Version check failed for %s: %s", agent_name, "; ".join(errors))
        raise RegistryError("; ".join(errors))


@dataclass(frozen=True)
class _CommandResult:
    success: bool
    output: str
    error: str


def _run_builder(image_ref: str, definition_dir: Path, global_cfg: GlobalConfig) -> _CommandResult:
    _ensure_version_check_image(image_ref, global_cfg, get_logger())
    process = run_builder_version_check(image_ref, definition_dir)
    return _from_process(process, "builder image")


def _run_host(script_path: Path) -> _CommandResult:
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


def _ensure_version_check_image(image_ref: str, global_cfg: GlobalConfig, logger: Logger) -> None:
    local_image, remote_image = _version_check_images(image_ref, global_cfg)
    local_digest = get_local_repo_digest(local_image)
    if local_digest is None:
        _pull_version_check_image(image_ref, logger)
        return

    remote_digest = get_remote_repo_digest(remote_image)
    if remote_digest is None or remote_digest == local_digest:
        return

    _pull_version_check_image(image_ref, logger)


def _pull_version_check_image(image_ref: str, logger: Logger) -> None:
    log_path = pull_log_path(image_ref)
    try:
        run_pull(image_ref, log_path)
    except RegistryError:
        logger.warning("Version check image pull failed; using local image (logs: %s).", log_path)


def _version_check_images(
    image_ref: str, global_cfg: GlobalConfig
) -> tuple[ImageRefRepository, RemoteImageRef]:
    registry, repository = _split_image_ref(image_ref, global_cfg.image_registry)
    local_repository = f"{registry}/{repository}" if registry else repository
    local_image = ImageRefRepository(image_ref=image_ref, repository=local_repository)
    remote_image = RemoteImageRef(
        image=ImageRefRepository(image_ref=image_ref, repository=repository),
        registry_api=RegistryApiConfig(
            registry_api_url=global_cfg.image_registry_api_url,
            registry_api_token_url=global_cfg.image_registry_api_token_url,
        ),
    )
    return local_image, remote_image


def _split_image_ref(image_ref: str, default_registry: str) -> tuple[str, str]:
    name = _strip_reference(image_ref)
    parts = name.split("/", 1)
    if len(parts) == 1:
        return default_registry, name
    registry, remainder = parts
    if "." in registry or ":" in registry or registry == "localhost":
        return registry, remainder
    return default_registry, name


def _strip_reference(image_ref: str) -> str:
    if "@" in image_ref:
        return image_ref.split("@", 1)[0]
    last_colon = image_ref.rfind(":")
    if last_colon > image_ref.rfind("/"):
        return image_ref[:last_colon]
    return image_ref
