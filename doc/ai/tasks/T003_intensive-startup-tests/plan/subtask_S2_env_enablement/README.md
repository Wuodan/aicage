# Task T003 / Subtask S2 — Environment & Tooling Readiness

## Objective
Verify the local environment (docker, buildx, bats, QEMU) and scripts required for agent startup exercises, capturing reproducible commands + troubleshooting steps in the plan.

## Deliverables
- Logged outputs for `docker info`, `bats --version`, and any builder/bootstrap commands, stored in the subtask plan.
- Notes on available base images, registries, and required env vars (API placeholders) for upcoming tests.
- Updated Flow/Checklist statuses plus Feedback capturing constraints or blockers (e.g., missing Docker socket access).

## Flow
1. Run `docker info` and `bats --version`, recording sanitized outputs in the plan.
2. Inspect `scripts/dev/bootstrap.sh`, `scripts/build.sh`, and `scripts/test.sh` to confirm required arguments/env vars; document how to invoke them per base/tool.
3. Validate BuildKit/bake availability (dry-run or `docker buildx bake --print`) without launching long builds yet.
4. Capture any credential or network requirements for agent CLIs; prepare placeholder env vars/secrets list.
5. Update plan checklists + Feedback, then commit `[codex][subtask-S2_env_enablement]: summary` once done.

## Checklist
- [ ] `docker info` + `bats --version` captured and logged.
- [ ] Script entrypoints + required flags documented.
- [ ] Builder/bake readiness confirmed (or blockers recorded).
- [ ] Document findings in Feedback.
- [ ] Commit `[codex][subtask-S2_env_enablement]: summary`.

## Inputs & References
- `scripts/dev/bootstrap.sh`, `scripts/build.sh`, `scripts/test.sh`
- `doc/ai/tasks/T003_intensive-startup-tests/README.md`
- `AGENTS.md`

## Exit Criteria
- Environment checks completed or blockers documented, plan updated with logs/notes, and Feedback highlights any gaps before running agent startups.

## Feedback & Learnings
- **Open Problems**: _TBD_
- **Questions**: _TBD_
- **Learnings**: _TBD_
