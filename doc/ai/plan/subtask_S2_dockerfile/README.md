# Subtask S2 — Parameterized Dockerfile

## Objective
Create a single `Dockerfile` that can build every base/tool combination via `BASE_IMAGE`, `TOOL`, and
`TARGETARCH` args, with clearly documented extension points and reliable installer logic for each
agent.

## Deliverables
- Root `Dockerfile` covering:
  - Base image preparation (packages, shared tooling).
  - Tool-specific installation blocks (`case "${TOOL}" in ...`).
  - Comments that highlight where to add new bases or agents.
- Documentation references in `README.md` (temporary note acceptable until S5).
- Smoke validation via `docker build --build-arg BASE_IMAGE=... --build-arg TOOL=...`.

## Flow
1. **Research installers**: Confirm CLI/agent installation steps for `cline`, `codex`, and
   `factory_ai_droid`. If unclear, use MCP `brave-search` → `fetch` and summarize findings in this
   file under *Feedback & Learnings*.
2. Define shared base setup (apt packages, locale fixes, user settings) compatible with all bases.
3. Implement tool install sections using Bash functions or `case` statements; fail fast on unknown
   tools.
4. Add comments `# Add new base tweaks here` and `# Add new agent installers below`.
5. Build at least one variant locally (amd64) to ensure syntax correctness.
6. Capture any user-facing implications (notes for README) here rather than editing README mid-task.
7. Update this checklist and plan log, then commit `[codex][dockerfile]: add parameterized build`.

## Checklist
- [ ] Installer research recorded for all tools (links + summary).
- [ ] Dockerfile base prep implemented with shared dependencies.
- [ ] Tool-specific install logic implemented and linted.
- [ ] Sample build succeeds (`docker build ...`).
- [ ] Plan + checklist updated; commit `[codex][dockerfile]: add parameterized build]`.

## Inputs & References
- `doc/ai/TASK.md` — required bases/tools list.
- `AGENTS.md` — Dockerfile conventions.
- External installer docs (cite URLs in Feedback).

## Exit Criteria
- All checklist items complete.
- Dockerfile ready for integration with Bake matrix.

## Feedback & Learnings
- _Pending._
