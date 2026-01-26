# Subtask 16-06 summary

## Context

- Subtask id and title: 16-06 - Untangle logic for extensions.
- Related subtasks touched or impacted: 16-03, 16-04, 16-06.

## Changes

- Key decisions (why): Extensions are a strict post-step; extension logic only depends on the guaranteed-local base+agent
  image ref and extension metadata. Entry point flow is a single ensure call. Pass explicit image refs instead of copying
  RunConfig.
- User-visible behavior changes: None.
- Internal behavior changes: Extension build decision ignores base/agent/version details; base-layer check is shared;
  pull/build decisions use explicit image refs; pull decision now returns a boolean.
- Files and modules with major changes:
  - doc/ai/task/16/16-06-SUBTASK-untangle-extension-logic-to-serial.md
  - src/aicage/cli/entrypoint.py
  - src/aicage/registry/ensure_image.py
  - src/aicage/registry/_pull_decision.py
  - src/aicage/registry/image_pull.py
  - src/aicage/registry/local_build/_layers.py
  - src/aicage/registry/local_build/_plan.py
  - src/aicage/registry/local_build/_extended_plan.py
  - src/aicage/registry/local_build/ensure_extended_image.py
  - src/aicage/registry/local_build/ensure_local_image.py

## Testing and validation

- Tests run: `pytest --cov=src --cov-report=term-missing`; `scripts/lint.sh`.
- Gaps or skipped tests and why: Integration tests skipped by default.

## Follow-ups

- Deferred items (explicitly list): None.
- Known risks or open questions: None.
- Suggested next steps: Review and verify extension builds against local images.

## Notes

- Lessons learned: Keep extension logic strictly post-step and pass explicit image refs to avoid config copying.
- Review feedback to carry forward: Keep entrypoint logic minimal; avoid pulling internal details upward.
