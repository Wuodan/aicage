# Task Index & Numbering

## Numbering Scheme
- Tasks use identifiers `T###` (e.g., `T001`, `T002`).
- Folder naming pattern: `doc/ai/tasks/T###_<slug>/` for archived tasks; `doc/ai/tasks/current/` points to the active one.
- Each task must provide:
  - `README.md` with objective, scope, timeline pointers, and cross-links to `doc/ai/TASK.md` (canonical brief).
  - Links to planning artifacts (e.g., `doc/ai/plan/`) and commits.
  - Feedback section capturing open problems, unanswered questions, and lessons learned.

## Current Task Folder
- `doc/ai/tasks/current/` mirrors the live task (`doc/ai/TASK.md`) and tracks status quick facts.
- When a task closes, move its folder to `doc/ai/tasks/T###_<slug>/` and update this index.

## Historical Log
| Task ID | Title | Status | Notes |
|---------|-------|--------|-------|
| T001 | Build the llm-agent-dock Matrix Builder | Active | See `doc/ai/tasks/current/README.md`.

Update this table as tasks finish or new ones start. Always keep `doc/ai/TASK.md` aligned with the active task ID.
