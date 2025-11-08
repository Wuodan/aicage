# Task T004 / Subtask S3 — Checklist & Template Propagation

## Objective
Update task and subtask planning templates (and any other reusable checklists) so that the new branching workflow steps become part of every future effort.

## Deliverables
- Revised `doc/ai/templates/task_plan_README.template.md` and `doc/ai/templates/subtask_plan_README.template.md` as needed to mention branch workflow checkpoints.
- Any additional checklist snippets (e.g., doc/ai/tasks/README instructions) referencing the process.
- Updated plan + Feedback entries capturing what changed and outstanding follow-ups.

## Flow
1. Review S1 decisions and AGENTS.md updates to identify which parts must be enforced via templates vs. referenced as links.
2. Update template sections (workflow guardrails, checklist bullets) to include branch creation/push/merge steps and reminders to log commands/tests.
3. Verify that templated checklists still fit within AGENTS.md expectations (objective/deliverables/flow/feedback).
4. No automated tests required; proofread Markdown and ensure placeholders remain clear.
5. Update plan checklist + Feedback as progress is made.
6. Commit `[codex][subtask_S3_checklists]: summary` once the templates and docs are updated.

## Checklist
- [ ] Identify every template/checklist that needs branch workflow references.
- [ ] Apply updates ensuring placeholders remain generic yet prescriptive.
- [ ] Cross-check against AGENTS.md to prevent conflicting guidance.
- [ ] Document findings in Feedback.
- [ ] Commit `[codex][subtask_S3_checklists]: summary`.

## Inputs & References
- `doc/ai/templates/task_plan_README.template.md`
- `doc/ai/templates/subtask_plan_README.template.md`
- `doc/ai/tasks/T004_branch-workflow-discipline/plan/subtask_S1_branch-policy/README.md`
- `doc/ai/tasks/T004_branch-workflow-discipline/plan/subtask_S2_doc-updates/README.md`

## Exit Criteria
- Templates include the new workflow steps, plan feedback updated, and references validated.

## Feedback & Learnings
- **Open Problems**: _TBD_
- **Questions**: _TBD_
- **Learnings**: _TBD_
