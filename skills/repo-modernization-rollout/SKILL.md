---
name: "repo-modernization-rollout"
description: "Phased modernization rollout for a private OpenCode agent fleet: governance constitution, failure-mode memory, slash prompts, agent consolidation, MCP prompt pilots, pre-commit validators, eval-nightly harness, cost report, trajectory viewer, and closeout crystallization. Agent repo modernization, OpenCode agents, 分波治理升级, agent 合并, MCP prompts, validator, eval harness, 成本统计, 轨迹 JSONL, 技能固化."
revision: 1
---

# Repo Modernization Rollout

> Crystallized from: repo-modernization-rollout Wave A/B/C execution — governance foundation, safe partial consolidation, MCP prompt pilots, and Wave C observability utilities.
> Date: 2026-05-24
> Trigger: T1

## When to Use

- A private OpenCode agent fleet needs a **phased modernization rollout** rather than ad-hoc edits.
- The work combines governance docs, agent prompt changes, validation scripts, MCP prompt pilots, and closeout artifacts.
- An agent consolidation wave is proposed and must be filtered through audit evidence plus Critical Thinking validation.
- You need to add local-only observability helpers such as eval smoke entrypoints, cost summaries, or debug trajectory viewers without introducing CI or external services.
- The rollout should produce per-task commits, a closeout report, and a reusable skill/memory record.

## When NOT to Use

- A single `*.md` needs small iterative feedback edits; use `agent-iterative-refinement` instead.
- The task is only tool-budget trimming; use `agent-tool-budget-trim` instead.
- The task is only role-boundary centralization without eval/cost/trajectory work; use `agent-fleet-boundary-cleanup` instead.
- The task is general VS Code customization or creating a brand-new agent file; use the built-in `agent-customization` skill.
- The user asks for public release automation or CI. This repo is private and local-use oriented unless the user explicitly changes that boundary.

## Workflow

### Phase 0 — Freeze the target and constraints

1. Read the active plan under `.github/plans/` and identify the first uncompleted task by `✅` markers plus `git log` evidence.
2. Record the current branch, agent count, and relevant untracked files. Do not touch unrelated untracked work.
3. Load only the sections needed for the current wave. Keep Minimal Viable Information discipline to avoid drowning later tasks in old context.
4. If the plan validator rejects legacy IDs, treat that as schema drift unless the current task is to upgrade the schema.

### Phase 1 — Governance and validators

1. Add or update governance artifacts first: constitution, known failure modes, See Also anchors, and validation scripts.
2. Run portfolio validation after every governance change.
3. Prefer stdlib-only Python scripts for repo governance checks. Follow the existing 0/1/2 or PASS/WARN/FAIL convention in adjacent scripts.
4. Commit each independent governance task before starting the next one.

### Phase 2 — Consolidation audit before deletion

1. Build a candidate ledger for every proposed merge/delete action.
2. Send the ledger to Critical Thinking and require a verdict per candidate: `OK`, `REJECT`, or `RECONSIDER`.
3. Execute only `OK` candidates unless the user explicitly accepts a riskier scope.
4. After each merge/delete, run the relevant validators and commit immediately.
5. Record skipped candidates and the reason in a closeout artifact.

### Phase 3 — MCP prompt pilots and hook hardening

1. Verify the target MCP server's actual prompt API before writing code. For FastMCP, use `@mcp.prompt(...)`.
2. Register prompts before `mcp.run()` / `main()`.
3. Validate prompt discovery through direct code inspection and existing smoke tests.
4. Extend pre-commit hooks only with checks that can run locally and deterministically.

### Phase 4 — Local observability utilities

1. For eval orchestration, call existing runner scripts with the repo's local interpreter. Prefer `.venv/bin/python`; do not use `source` activation or nonexistent wrappers.
2. Keep cost-report and trajectory tools read-only, stdlib-only, and explicit about empty-input behavior.
3. Make debug trajectory capture opt-in with `--trace-agent-run`; never treat a trace file as the completion source of truth.
4. Add targeted edge-case tests: empty input, bad JSON/JSONL, missing files, and regression exit codes.

### Phase 5 — Closeout and crystallization

1. Run the full validator suite and capture concise evidence.
2. Create `.github/reviews/<rollout-closeout>.md` with shipped work, deferred items, validator state, lessons, and follow-ups.
3. Create or update `skills/<skill-name>/SKILL.md` using `docs/skill-crystallization.md` as the template.
4. Append the skill to `memories/repo/crystallized-skills.md`.
5. Mark the final plan task complete and commit only the current task files.

## Inputs & Outputs

| Input | Source |
|-------|--------|
| Rollout plan | `.github/plans/repo-modernization-rollout.md` |
| Current completion state | `✅` markers plus `git log --oneline` |
| Agent inventory | `ls *.md`, README registry, validator summaries |
| Existing validation behavior | `scripts/validate-portfolio.sh`, `check_agent_tool_budget.py`, delegation and graph scripts |
| MCP prompt implementation evidence | Server files in sibling repos such as `manuscript-lint` and `de-ai-fier` |
| Closeout evidence | Validator outputs captured near the end of the rollout |

| Output | Format |
|--------|--------|
| Updated governance / agent files | Markdown agent, instruction, review, and memory files |
| Utility scripts | Stdlib-only Python under `scripts/` or target repo script path |
| Per-task commits | One scoped commit per completed task; no push |
| Closeout report | `.github/reviews/repo-modernization-closeout-2026.md` |
| Crystallized skill | `skills/repo-modernization-rollout/SKILL.md` |
| Skill registry row | `memories/repo/crystallized-skills.md` |

## Common Pitfalls

- **Broad `grep FAIL` creates false positives**: `check_agent_tool_budget.py` can contain header or explanatory text with `FAIL`. Use `awk '$NF=="FAIL"{bad=1} END{exit bad?1:0}'` to test the status column.
- **FastMCP prompt API name drift**: FastMCP prompts use `@mcp.prompt(...)`, not guessed alternatives. Register prompt functions before `mcp.run()` / `main()`.
- **Name-similar agents are not automatically mergeable**: agent consolidation must pass CT validation against contracts, tool authority, and delegation behavior. Names alone are weak evidence.
- **Makefile eval wrappers can fossilize wrong assumptions**: do not use `source` or point to nonexistent `run.sh`. Call the actual runner with `.venv/bin/python`.
- **Unrelated untracked files are easy to sweep into commits**: always `git add` explicit paths for the current task only.
- **Plan schema warnings can be non-blocking in legacy plans**: if the validator rejects legacy IDs but the current task is not schema migration, record it and continue using plan headings plus commit evidence.
- **Trajectory logs are not audit logs**: `.agent-runs/` is debug-only and opt-in. Do not make execution success depend on trace write success.
- **Closeout placeholders can leak into deliverables**: run a grep check for placeholder tokens before committing.

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-05-24 | Initial crystallization | repo-modernization-rollout Wave A/B/C: governance foundation, safe partial consolidation 40→36, MCP prompt pilots, pre-commit gates, eval-nightly harness, cost report, trajectory viewer, and closeout report |
