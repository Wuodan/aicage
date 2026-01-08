# Task 15 summary

## Context

- Task id and title: 15 - Local build base-image digest validation.
- Related tasks touched or impacted: 14.

## Changes

- Key decisions (why): Align local rebuild detection with the `aicage-image` refresh workflow by validating base image
  inclusion via the last base layer in the local final image; remove stored base digest state entirely to avoid stale
  text records.
- User-visible behavior changes: Local built images rebuild when the base image tag points to a new base layer that is
  not present in the local final image; base-image digest text state is no longer used.
- Internal behavior changes: Local builds now pull the base image on remote digest changes, then validate base-layer
  inclusion via local Docker RootFS layers; build records no longer persist base digests.
- Files and modules with major changes:
  - src/aicage/registry/local_build/_layers.py
  - src/aicage/registry/local_build/_plan.py
  - src/aicage/registry/local_build/_store.py
  - src/aicage/registry/local_build/ensure_local_image.py
  - tests/aicage/integration/local_builtin/test_rebuild_base_layer.py
  - tests/aicage/integration/local_custom/test_rebuild_base_layer.py
  - tests/aicage/registry/local_build/test_plan.py
  - tests/aicage/registry/local_build/test_store.py
  - doc/integration-tests.md
  - CHANGELOG.md

## Testing and validation

- Tests run:
  - `pytest --cov=src --cov-report=term-missing`
  - `./scripts/lint.sh`
- Gaps or skipped tests and why: Integration tests were skipped (require `AICAGE_RUN_INTEGRATION=1`).

## Follow-ups

- Deferred items (explicitly list): None.
- Known risks or open questions: Layer validation is skipped when local layer data is unavailable; a warning is logged.

## Notes

- Lessons learned: Use local layer inspection to validate base image inclusion for locally built final images.
- Review feedback to carry forward: Avoid storing base image digests in local state.
