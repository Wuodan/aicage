from __future__ import annotations

from pathlib import Path

from ._tty import ensure_tty_for_prompt


def prompt_for_missing_extensions(
    agent: str,
    missing: list[str],
    stored_image_ref: str,
    project_config_path: Path,
    other_projects: list[tuple[str, Path]],
) -> str:
    ensure_tty_for_prompt()
    print(f"[aicage] Missing extensions for '{agent}': {', '.join(sorted(missing))}.")
    if stored_image_ref:
        print(f"[aicage] Stored image ref: {stored_image_ref}")
    print(f"[aicage] Project config: {project_config_path}")
    if other_projects:
        print("[aicage] Other projects using this image:")
        for project_path, config_path in other_projects:
            print(f"  {project_path} -> {config_path}")
    return input("Choose 'exit' or 'fresh': ").strip().lower()
