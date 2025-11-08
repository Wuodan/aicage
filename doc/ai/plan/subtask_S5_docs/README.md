# Subtask S5 — Documentation & Polish

## Objective
Align all written guidance with the implemented build system so newcomers can understand the matrix,
run commands, extend bases/tools, and trace decisions via planning docs.

## Deliverables
- Updated root `README.md`:
  - Overview of architecture, matrix table, and automation commands.
  - Quick-start instructions for bootstrap/build/test scripts.
  - Extension guides for adding bases and tools (per AGENTS.md expectations).
- Any supporting docs (e.g., `doc/terraform` equivalent for this repo if needed) plus references to
  planning entries.
- Finalized plan docs reflecting completion (checklists + feedback).

## Flow
1. Audit actual implementation artifacts (Dockerfile, Bake file, scripts, tests).
2. Update README sections (goal, architecture, commands, extension steps, testing).
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
