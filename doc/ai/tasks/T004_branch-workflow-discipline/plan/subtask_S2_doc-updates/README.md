# Task T004 / Subtask S2 — Update AGENTS.md & Related Docs

## Objective
Propagate the approved branch workflow policies into AGENTS.md and any other contributor-facing docs that mention branching, merging, or commit practices.

## Deliverables
- Revised `AGENTS.md` describing branch naming, push cadence, merge method, and deletion rules.
- Any supplemental updates to task descriptions or README files referencing the workflow (link them here).
- Updated plan + Feedback section summarizing what changed and why.

## Flow
1. Pull finalized decisions from S1 and map each policy to the sections in AGENTS.md that need edits (workflow hardening, testing, commit/PR expectations).
2. Update AGENTS.md with concise instructions, ensuring they align with repository tone and cite required commands (e.g., `git merge --no-ff`).
3. Adjust other docs if they duplicate workflow guidance (e.g., root README, task index) and cross-link to AGENTS.md instead of duplicating text.
4. Run formatting/lint checks if applicable (Markdown lint manual review; no automated tests required but proofread links/paths).
5. Update plan checklist + Feedback; ensure research references (if any) are logged.
6. Commit `[codex][subtask_S2_doc-updates]: summary` once all checklist items complete.

## Checklist
- [ ] Map S1 decisions to specific documentation sections needing updates.
- [ ] Apply edits to AGENTS.md (and other docs, if needed) with consistent naming + flow instructions.
- [ ] Self-review for clarity/formatting; capture summary in plan Feedback.
- [ ] Document findings in Feedback.
- [ ] Commit `[codex][subtask_S2_doc-updates]: summary`.

## Inputs & References
- `doc/ai/tasks/T004_branch-workflow-discipline/README.md`
- `doc/ai/tasks/T004_branch-workflow-discipline/plan/subtask_S1_branch-policy/README.md`
- `AGENTS.md`

## Exit Criteria
- All targeted docs mention the new workflow, references are updated, and plan feedback reflects completion.

## Feedback & Learnings
- **Open Problems**: _TBD_
- **Questions**: _TBD_
- **Learnings**: _TBD_
