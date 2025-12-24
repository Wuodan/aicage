import subprocess
import sys
from dataclasses import dataclass

from aicage.config.context import ConfigContext
from aicage.errors import CliError
from aicage.runtime.prompts import BaseSelectionRequest, prompt_for_base

from .discovery.catalog import discover_tool_bases

__all__ = ["pull_image", "select_tool_image"]


def pull_image(image_ref: str) -> None:
    pull_result = _stream_docker_pull(image_ref)

    if pull_result.returncode == 0:
        if not pull_result.showed_output and pull_result.up_to_date:
            print(f"[aicage] Image {image_ref} is up to date.")
        return

    inspect = subprocess.run(
        ["docker", "image", "inspect", image_ref],
        check=False,
        capture_output=True,
        text=True,
    )
    if inspect.returncode == 0:
        msg = pull_result.last_nonempty_line or f"docker pull failed for {image_ref}"
        print(f"[aicage] Warning: {msg}. Using local image.", file=sys.stderr)
        return

    detail = pull_result.last_nonempty_line or f"docker pull failed for {image_ref}"
    raise CliError(detail)


@dataclass(frozen=True)
class _PullResult:
    returncode: int
    last_nonempty_line: str
    showed_output: bool
    up_to_date: bool


def _is_progress_line(line: str) -> bool:
    return any(
        marker in line
        for marker in (
            "Pulling fs layer",
            "Downloading",
            "Extracting",
            "Waiting",
            "Download complete",
            "Pull complete",
            "Downloaded newer image",
        )
    )


def _stream_docker_pull(image_ref: str) -> _PullResult:
    show_output = False
    up_to_date = False
    buffered_lines: list[str] = []
    last_nonempty_line = ""
    pull_process = subprocess.Popen(
        ["docker", "pull", image_ref],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    if pull_process.stdout is not None:
        for line in pull_process.stdout:
            if show_output:
                sys.stdout.write(line)
                sys.stdout.flush()
            else:
                buffered_lines.append(line)

            stripped = line.strip()
            if not stripped:
                continue
            last_nonempty_line = stripped
            if "Image is up to date" in stripped:
                up_to_date = True
            if not show_output and _is_progress_line(stripped):
                show_output = True
                print(f"[aicage] Pulling image {image_ref}...")
                sys.stdout.write("".join(buffered_lines))
                sys.stdout.flush()
                buffered_lines = []

    pull_process.wait()

    return _PullResult(
        returncode=pull_process.returncode,
        last_nonempty_line=last_nonempty_line,
        showed_output=show_output,
        up_to_date=up_to_date,
    )


def select_tool_image(tool: str, context: ConfigContext) -> str:
    tool_cfg = context.project_cfg.tools.setdefault(tool, {})
    base = tool_cfg.get("base") or context.global_cfg.tools.get(tool, {}).get("base")
    repository_ref = context.image_repository_ref()

    if not base:
        available_bases = discover_tool_bases(context, tool)
        if not available_bases:
            raise CliError(f"No base images found for tool '{tool}' (repository={repository_ref}).")

        request = BaseSelectionRequest(
            tool=tool,
            default_base=context.global_cfg.default_image_base,
            available=available_bases,
        )
        base = prompt_for_base(request)
        tool_cfg["base"] = base
        context.store.save_project(context.project_path, context.project_cfg)

    image_tag = f"{tool}-{base}-latest"
    image_ref = f"{repository_ref}:{image_tag}"
    return image_ref
