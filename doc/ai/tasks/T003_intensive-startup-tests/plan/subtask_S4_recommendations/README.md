# Task T003 / Subtask S4 — Recommendations & Documentation Updates

## Objective
Consolidate findings from S1–S3 into actionable recommendations, propose Dockerfile/test/script adjustments, and update all Feedback sections + downstream docs so future agents can reproduce the startup harness.

## Deliverables
- Summary of startup observations + required fixes within this subtask README (and referenced artifacts under `plan/`).
- List of proposed patches (Dockerfiles, tests, docs) with prioritization, including any quick fixes implemented during this task.
- Updated Feedback sections across task + subtasks, plus any new research notes or troubleshooting guides.
- Commit `[codex][subtask-S4_recommendations]: summary` capturing doc/code updates.

## Flow
1. Aggregate logs + notes from S3 to identify recurring issues (auth prompts, missing deps, log streaming blockers).
2. Draft recommended changes (Dockerfile tweaks, test harness updates, env var docs) and implement low-risk patches if in scope.
3. Update task-level Notes/Progress/References with links to new artifacts; ensure sanitized logs are referenced.
4. Review entire plan for completeness, fill Feedback with lessons + open problems, and capture follow-on tasks if needed.
5. Commit `[codex][subtask-S4_recommendations]: summary` after verifying documentation + code changes.

## Checklist
- [ ] Findings synthesized into prioritized recommendations.
- [ ] Plan + Feedback sections updated across task + subtasks.
- [ ] Required doc/code patches applied or queued with clear follow-up steps.
- [ ] Document findings in Feedback.
- [ ] Commit `[codex][subtask-S4_recommendations]: summary`.

## Inputs & References
- Outputs from S1–S3.
- `AGENTS.md`, task README, and any research logs.

## Exit Criteria
- T003 plan reflects final status, recommendations captured, and downstream files updated such that the next agent can act without ambiguity.

## Feedback & Learnings
- **Open Problems**: _TBD_
- **Questions**: _TBD_
- **Learnings**: _TBD_
