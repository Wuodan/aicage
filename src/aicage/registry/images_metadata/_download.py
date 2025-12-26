from __future__ import annotations

import json
import urllib.request
from typing import Any

from aicage.config.global_config import GlobalConfig
from aicage.errors import CliError


def download_images_metadata(global_cfg: GlobalConfig) -> str:
    release = _fetch_json(global_cfg.images_metadata_release_api_url)
    asset_url = _find_asset_download_url(release, global_cfg.images_metadata_asset_name)
    return _fetch_text(asset_url)


def _fetch_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(request) as response:
            payload = response.read().decode("utf-8")
    except Exception as exc:  # pylint: disable=broad-except
        raise CliError(f"Failed to fetch release metadata from {url}: {exc}") from exc
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise CliError(f"Invalid JSON from {url}: {exc}") from exc
    if not isinstance(data, dict):
        raise CliError(f"Release metadata from {url} must be an object.")
    return data


def _find_asset_download_url(release: dict[str, Any], asset_name: str) -> str:
    assets = release.get("assets", [])
    if not isinstance(assets, list):
        raise CliError("Release metadata 'assets' must be a list.")
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        if asset.get("name") == asset_name:
            download_url = asset.get("browser_download_url")
            if isinstance(download_url, str) and download_url.strip():
                return download_url
    raise CliError(f"Release asset '{asset_name}' not found.")


def _fetch_text(url: str) -> str:
    request = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(request) as response:
            return response.read().decode("utf-8")
    except Exception as exc:  # pylint: disable=broad-except
        raise CliError(f"Failed to download images metadata from {url}: {exc}") from exc
