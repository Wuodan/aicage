# Subtask summary

## Context

- Subtask id and title: 17-03 Adapt image pull/check/build to ConfigContext data
- Related subtasks touched or impacted: 17-02 (selection/context usage), future 17-04 docs

## Changes

- Key decisions (why): remove `images_metadata` entirely so runtime paths trust `RunConfig` and ConfigContext, keeping
  validation only in early selection.
- User-visible behavior changes: none intended; image selection/build should follow existing choices and pulls.
- Internal behavior changes: moved agent/base metadata models into `config/agent/models.py` and `config/base/models.py`,
  moved base filtering to `config/base/filter.py`, removed `images_metadata` package and config files, and switched
  runtime agent config to use trusted metadata directly.
- Files and modules with major changes: `src/aicage/config/context.py`, `src/aicage/runtime/_agent_config.py`,
  `src/aicage/registry/ensure_image.py`, `src/aicage/registry/local_build/ensure_local_image.py`,
  `src/aicage/config/agent/models.py`, `src/aicage/config/base/models.py`, `src/aicage/config/base/filter.py`.

## Testing and validation

- Tests run: `pytest --cov=src --cov-report=term-missing`, `scripts/lint.sh`.
- Gaps or skipped tests and why: integration tests skipped by markers (26 skipped).

## Follow-ups

- Deferred items (explicitly list): none.
- Known risks or open questions: ensure documentation updates in subtask 17-04 reflect removed `images-metadata.yaml`.
- Suggested next steps: proceed with subtask 17-04 documentation updates.

## Notes

- Lessons learned: keep validation centralized in `load_run_config` and avoid re-checking trusted runtime config.
- Review feedback to carry forward: use `ruff check . --fix` for import reordering when fixable.
