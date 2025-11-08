# Task T004 — Enforce Branch Workflow & Merge Discipline

## Status
- Status: Proposed (plan pending)
- Owner: TBD
- Links: _(Plan folder will be created once scheduled)_

## Background
The repo currently allows direct work on `development`, ad-hoc amends, and history edits. We need a
repeatable workflow where every task/subtask runs on its own branch, merges upstream via
`git merge --no-ff`, and deletes branches only after merges are confirmed locally and remotely.
This is a prerequisite for future policy changes that may forbid rewriting history entirely.

## Goals & Deliverables
1. Update AI-facing docs (e.g., `AGENTS.md`, planning templates) to specify:
   - Naming conventions for task/subtask branches (e.g., `task/T004_branch-workflow` and
     `task/T004_S1_planning`).
   - Required flow: create branch → push to GitHub → do work → merge back into the parent branch via
     a single, consistent method (either **always** local `git merge --no-ff` or **always** a GitHub
     pull request; pick one and document it—no dual-path ambiguity).
   - Subtasks merge into their parent task branch; tasks merge into `development` the same way.
   - Branch deletion rules (local + remote) only after verifying merges.
2. Document expectations around pushing frequency and when force-push is acceptable. Investigate the
   current “amend latest commit” habit; either discourage it or carve out explicit exceptions.
3. Provide a concise checklist future agents can follow before finishing a subtask/task (e.g., tests
   run, branch pushed, merge performed, branch deleted).

## Out of Scope
- Implementing CI checks; this task is purely about documentation/process updates.
- Rewriting existing history—focus on forward-going guidelines.

## Dependencies & Inputs
- Existing guidance in `AGENTS.md` and task templates.
- Current git practices noted during T003 (amend-on-last-commit behavior).

## Open Questions
- Exact branch naming format (prefix `task/` vs `T###/`). Decide during planning.
- Whether task branches require PRs or can merge locally with logs documenting the merge.

## Next Steps
- Kick off planning per AGENTS.md templates when scheduled.
