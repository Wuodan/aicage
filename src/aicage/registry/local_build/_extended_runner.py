from __future__ import annotations

import subprocess
from pathlib import Path

from aicage._logging import get_logger
from aicage.config.resources import find_packaged_path
from aicage.config.runtime_config import RunConfig
from aicage.errors import CliError
from aicage.registry._extensions import ExtensionMetadata


def run_extended_build(
    run_config: RunConfig,
    base_image_ref: str,
    extensions: list[ExtensionMetadata],
    log_path: Path,
) -> None:
    logger = get_logger()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[aicage] Building extended image {run_config.image_ref} (logs: {log_path})...")
    logger.info("Building extended image %s (logs: %s)", run_config.image_ref, log_path)

    dockerfile_builtin = find_packaged_path("extension-build/Dockerfile")
    current_image_ref = base_image_ref
    with log_path.open("w", encoding="utf-8") as log_handle:
        for idx, extension in enumerate(extensions):
            target_ref = (
                run_config.image_ref
                if idx == len(extensions) - 1
                else _intermediate_image_ref(run_config, extension, idx)
            )
            dockerfile_path = extension.dockerfile_path or dockerfile_builtin
            command = [
                "docker",
                "build",
                "--no-cache",
                "--file",
                str(dockerfile_path),
                "--build-arg",
                f"BASE_IMAGE={current_image_ref}",
                "--build-arg",
                f"EXTENSION={extension.extension_id}",
                "--tag",
                target_ref,
                str(extension.directory),
            ]
            result = subprocess.run(command, check=False, stdout=log_handle, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                logger.error(
                    "Extended image build failed for %s (logs: %s)",
                    run_config.image_ref,
                    log_path,
                )
                raise CliError(
                    f"Extended image build failed for {run_config.image_ref}. See log at {log_path}."
                )
            current_image_ref = target_ref
    logger.info("Extended image build succeeded for %s", run_config.image_ref)


def _intermediate_image_ref(run_config: RunConfig, extension: ExtensionMetadata, idx: int) -> str:
    repository, _ = _parse_image_ref(run_config.image_ref)
    tag = f"tmp-{run_config.agent}-{run_config.base}-{idx + 1}-{extension.extension_id}"
    tag = tag.lower().replace("/", "-")
    return f"{repository}:{tag}"


def _parse_image_ref(image_ref: str) -> tuple[str, str]:
    repository, sep, tag = image_ref.rpartition(":")
    if not sep:
        return image_ref, "latest"
    return repository, tag
