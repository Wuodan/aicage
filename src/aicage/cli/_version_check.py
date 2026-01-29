import json
import re
import subprocess
import sys
import urllib.error
import urllib.request

from aicage._logging import get_logger

_PYPI_URL: str = "https://pypi.org/pypi/aicage/json"
_REQUEST_TIMEOUT_SECONDS: float = 2.5
_UPGRADE_COMMAND: str = "pipx upgrade aicage"


def _check_for_update(current_version: str) -> str | None:
    logger = get_logger()
    try:
        request = urllib.request.Request(_PYPI_URL, headers={"Accept": "application/json"})
        with urllib.request.urlopen(request, timeout=_REQUEST_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning("Version check failed: %s", exc)
        return None

    latest_version = str(payload.get("info", {}).get("version", "")).strip()
    if not latest_version:
        return None

    if _is_newer(latest_version, current_version):
        return latest_version

    return None


def maybe_prompt_update(current_version: str) -> None:
    latest_version = _check_for_update(current_version)
    if not latest_version:
        return

    print(
        "A newer version of aicage is available "
        f"(installed: {current_version}, latest: {latest_version})."
    )

    if not sys.stdin.isatty():
        print(f"Update with: {_UPGRADE_COMMAND}")
        return

    try:
        answer = input("Update now? [y/N] ").strip().lower()
    except EOFError:
        print(f"Update with: {_UPGRADE_COMMAND}")
        return

    if answer in {"y", "yes"}:
        _run_upgrade()
    else:
        print(f"Update with: {_UPGRADE_COMMAND}")


def _run_upgrade() -> None:
    logger = get_logger()
    try:
        result = subprocess.run(
            _UPGRADE_COMMAND.split(),
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        logger.error("Upgrade command failed: %s", exc)
        print(f"Unable to run '{_UPGRADE_COMMAND}'. Please run it manually.")
        return

    if result.returncode != 0:
        logger.error(
            "Upgrade command failed (%s): %s",
            result.returncode,
            result.stderr.strip(),
        )
        print(f"Upgrade failed. Please run '{_UPGRADE_COMMAND}' manually.")


def _is_newer(latest_version: str, current_version: str) -> bool:
    latest = _parse_version(latest_version)
    current = _parse_version(current_version)
    if latest is None or current is None:
        return False
    length = max(len(latest), len(current))
    latest_padded = latest + (0,) * (length - len(latest))
    current_padded = current + (0,) * (length - len(current))
    return latest_padded > current_padded


def _parse_version(version: str) -> tuple[int, ...] | None:
    match = re.match(r"^(\d+(?:\.\d+)*)", version)
    if not match:
        return None
    return tuple(int(part) for part in match.group(1).split("."))
