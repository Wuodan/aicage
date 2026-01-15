# Subtask summary

## Context

- Subtask id and title: 17-01-load-context (Load all bases and agents into ConfigContext)
- Related subtasks touched or impacted: 17-02 runtime prompts, 17-03 image process (future alignment with new context fields)

## Changes

- Key decisions (why): unify builtin and custom loaders for bases/agents so ConfigContext holds complete
  metadata; keep custom override behavior; enforce strict visibility by making internal-only modules private
- User-visible behavior changes: none expected; selection and runtime behavior remain the same
- Internal behavior changes: ConfigContext now includes all agents and bases; BaseMetadata/AgentMetadata
  normalized to non-null lists and definition paths; images_metadata loading no longer discovers agents/bases

## Testing and validation

- Tests run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt;
  pytest --cov=src --cov-report=term-missing
- Gaps or skipped tests and why: integration tests skipped by markers (existing behavior)

## Follow-ups

- Deferred items (explicitly list): update prompts and image process to use ConfigContext directly (Subtasks 17-02, 17-03)
- Known risks or open questions: ensure future visibility rules remain consistent as modules move/rename
- Suggested next steps: proceed to Subtask 17-02 after confirming visibility rules and module naming conventions

## Notes

- Lessons learned: keep private modules aligned with test file naming to satisfy structure rules
- Review feedback to carry forward: avoid __init__.py re-exports; default to private modules unless externally used
