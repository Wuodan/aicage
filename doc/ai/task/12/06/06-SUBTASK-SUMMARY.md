# Subtask 06 summary

## Context

- Subtask id and title: 06 - Custom local agents.
- Related subtasks touched or impacted: 01, 02, 04, 05.

## Changes

- Key decisions (why): Replace redistributable with build_local in metadata; custom agents default to local builds; simplify runtime logic by using local_definition_dir instead of multiple booleans.
- User-visible behavior changes: Users can define local agents under ~/.aicage/custom/agent/ and they are discovered, validated, version-checked, and built locally.
- Internal behavior changes: Custom agent validation uses packaged schema; missing install.sh/version.sh fails fast; local build path is selected via local_definition_dir; release workflows in aicage-image now use build_local for filtering.
- Files and modules with major changes:
  - src/aicage/registry/custom_agent/_validation.py
  - src/aicage/registry/custom_agent/loader.py
  - src/aicage/registry/images_metadata/models.py
  - src/aicage/registry/local_build/ensure_local_image.py
  - src/aicage/cli/entrypoint.py
  - aicage-image/.github/workflows/release.yml
  - aicage-image/.github/workflows/build.yml
  - aicage-image/.github/workflows/refresh-images.yml
  - CHANGELOG.md

## Testing and validation

- Tests run: pytest --cov=src --cov-report=term-missing; yamllint .; pymarkdown --config .pymarkdown.json scan .; ruff check .; pyright .; rg -n --glob '*.py' '__all__' src.
- Gaps or skipped tests and why: None.

## Follow-ups

- Deferred items (explicitly list): None.
- Known risks or open questions: None.
- Suggested next steps: Validate a custom local agent end-to-end on a fresh base image.

## Notes

- Lessons learned: Keep workflow filters aligned when renaming metadata fields.
- Review feedback to carry forward: Avoid redundant guards; keep changes minimal; do not paste code blocks in chat; only commit on explicit request.
