# Subtask summary

## Context

- Subtask id and title: 12/07 - Extensions for final images
- Related subtasks touched or impacted: Deferred items captured in
  doc/ai/task/12/09/09-SUBTASK.md

## Changes

- Key decisions (why): Extension metadata stays minimal (no optional fields); extended image naming uses
  `<agent>-<base>-<ext...>`; project config stores image refs for reuse; missing extensions prompt
  offers exit or fresh selection and lists other project configs using the same image ref.
- User-visible behavior changes: Extension selection is prompted on base choice; extended images can be
  selected directly; missing extension configs block with clear guidance; extended image build logs
  are surfaced.
- Internal behavior changes: Extension discovery and hashing; extended image config load/save; local
  build plan/runner/store for extended images; added robust prompt and selection flow tests; cleaned
  extension script run dir after execution.
- Files and modules with major changes: src/aicage/registry/_extensions.py,
  src/aicage/registry/_extended_images.py, src/aicage/registry/image_selection/selection.py,
  src/aicage/registry/image_selection/extensions/*, src/aicage/registry/local_build/*,
  src/aicage/runtime/prompts/*, doc/extensions.md, config/extension-build/Dockerfile,
  config/agent-build/Dockerfile, tests/aicage/**.

## Testing and validation

- Tests run: `.venv/bin/ruff check .`, `.venv/bin/pytest --cov=src --cov-report=term-missing`
- Gaps or skipped tests and why: None noted; integration tests run locally.

## Follow-ups

- Deferred items (explicitly list): Add a change-selection/reset flow
  (doc/ai/task/12/09/09-SUBTASK.md); consider supporting multiple images per agent in a project
  config (doc/ai/task/12/09/09-SUBTASK.md); add CI pipeline coverage for a minimal extension build.
- Known risks or open questions: None beyond deferred CI coverage.
- Suggested next steps: Implement deferred items when scheduled in Subtask 09.

## Notes

- Lessons learned: Avoid rewriting docs for linting; preserve Markdown semantics like trailing spaces; keep scope tight.
- Review feedback to carry forward: Respect visibility rules (private by default), avoid `__all__`,
  add tests for visibility checks, and avoid unnecessary public API/fields.
