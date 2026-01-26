# Subtask summary

## Context

- Subtask id and title: 17-02 runtime prompts (Adapt runtime prompting and selection to ConfigContext data)
- Related subtasks touched or impacted: 17-01 load context, 17-03 image process (base selection flow)

## Changes

- Key decisions (why): route runtime selection/prompts through ConfigContext to avoid images_metadata; centralize
  base exclude filtering in one helper; reduce argument sprawl by passing ConfigContext into selection helpers.
- User-visible behavior changes: base options are filtered by base_exclude and base_distro_exclude from agent metadata;
  extended images list remains per-agent.
- Internal behavior changes: selection/prompting now resolves agents/bases from ConfigContext, base refs are built without
  valid_bases, and missing-extension handling reads from context.
- Files and modules with major changes: src/aicage/registry/image_selection/_metadata.py,
  src/aicage/registry/image_selection/_fresh_selection.py,
  src/aicage/registry/image_selection/selection.py,
  src/aicage/registry/image_selection/extensions/extended_images.py,
  src/aicage/registry/image_selection/extensions/missing_extensions.py,
  src/aicage/registry/image_selection/extensions/refs.py,
  src/aicage/runtime/prompts/base.py,
  src/aicage/config/base_filter.py.

## Testing and validation

- Tests run: pytest --cov=src --cov-report=term-missing; scripts/lint.sh
- Gaps or skipped tests and why: integration tests skipped by markers (existing behavior).

## Follow-ups

- Deferred items (explicitly list): remove AgentMetadata.valid_bases from model and production code.
- Known risks or open questions: extended image options no longer re-check bases since fresh_selection validates bases.
- Suggested next steps: proceed to Subtask 17-03 and finish removal of valid_bases.

## Notes

- Lessons learned: sharing base filtering logic avoids drift between prompt and selection paths.
- Review feedback to carry forward: prefer passing ConfigContext over splitting into multiple parameters.
