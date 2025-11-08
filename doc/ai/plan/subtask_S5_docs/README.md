# Subtask S5 — Documentation & Polish

## Objective
Align all written guidance with the implemented build system so newcomers can understand the matrix,
run commands, extend bases/tools, and trace decisions via planning docs.

## Deliverables
- Updated root `README.md` (user-facing only) covering:
  - Concise overview + value prop.
  - Matrix table (bases/tools/platforms) and quick-start commands.
  - Extension guidance for adding bases/tools.
  - Pointer to contributor docs (`AGENTS.md`, `doc/ai/plan/`) without embedding process detail.
- Supporting contributor docs (if any) live under `doc/ai/` and reference the plan as needed.
- Finalized plan docs reflecting completion (checklists + feedback).

## Flow
1. Audit actual implementation artifacts (Dockerfile, Bake file, scripts, tests).
2. Update README sections (goal, architecture, commands, extension steps, testing) while keeping the
   tone user-centric.
3. Ensure plan + subtask docs reference final states and include lessons learned.
4. Proofread for clarity and alignment with AGENTS.md style (tables, ~100-char lines).
5. Commit `[codex][docs]: refresh usage + extension guide]`.

## Checklist
- [ ] Architecture + matrix documentation refreshed.
- [ ] Commands section synced with `scripts/`.
- [ ] Extension guidance updated (add base/tool instructions).
- [ ] Testing instructions reference `scripts/test.sh` and smoke suites.
- [ ] Plan + feedback sections finalized.
- [ ] Commit `[codex][docs]: refresh usage + extension guide]`.

## Inputs & References
- Outputs of S2–S4.
- Existing README content.

## Exit Criteria
- Documentation matches repo state and guides future contributors.

## Feedback & Learnings
- _Pending._
