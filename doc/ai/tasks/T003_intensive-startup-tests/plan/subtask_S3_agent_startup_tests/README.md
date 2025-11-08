# Task T003 / Subtask S3 — Agent Startup Capture

## Objective
Launch each agent CLI (`cline`, `codex`, `factory_ai_droid`) inside every supported base image (`ubuntu`, `act`, `universal`), observe startup prompts, and capture stdout/stderr behavior for CI-safe automation.

## Deliverables
- Reproduction commands (docker run/build/test invocations) per agent/base combo, documented in this subtask plan.
- Sanitized log snippets noting timing, prompts, auth requirements, and blocking conditions.
- Inventory of missing packages, required env vars, or config files uncovered during runs.
- Feedback entries summarizing issues + recommendations feeding S4.

## Flow
1. Build or pull the relevant agent images using `docker buildx bake` or `scripts/build.sh <tool> <base>` (respecting platform constraints noted in S2).
2. Start each container with non-interactive wrappers (e.g., `docker run --rm -i` with `script`/`stdbuf` or `pexpect` helper) to capture stdout/stderr asynchronously; log command + location of saved logs.
3. Document prompts/auth flows encountered; attempt bypass via env vars or placeholders without entering real credentials.
4. Note any missing dependencies or file paths; triage whether Dockerfile/test updates are needed.
5. Update checklists + Feedback, then commit `[codex][subtask-S3_agent_startup_tests]: summary` once all combos are covered or blockers recorded.


## Checklist
- [ ] All agent/base combos exercised or explicitly blocked with rationale.
- [ ] Logs + observations saved under `plan/` with timestamps.
- [ ] Auth prompt handling + env var strategy documented.
- [ ] Missing dependency list captured.
- [ ] Document findings in Feedback.
- [ ] Commit `[codex][subtask-S3_agent_startup_tests]: summary`.

## Inputs & References
- Scripts under `scripts/`.
- Task README + subtask S2 environment notes.
- Existing `tests/smoke/*.bats` for reference on invocation patterns.

## Exit Criteria
- Each agent/startup scenario evaluated with reproducible commands, logs stored, and Feedback summarizing outstanding failures or follow-ups.

## Feedback & Learnings
- **Open Problems**: _TBD_
- **Questions**: _TBD_
- **Learnings**: _TBD_
