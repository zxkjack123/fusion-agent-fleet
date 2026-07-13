---
name: "agent-fleet-governance-update"
description: "Cost-driven model routing rebalance + new static governance script + documentation hygiene across the agent fleet. Use when introducing a new/cheaper model tier (e.g. DeepSeek V4 Pro) and rerouting low-judgment specialists to it, OR when adding a new static checker script (delegation graph / model allowlist), OR when extracting accumulated version history into a CHANGELOG. Three-pillar pattern: Pillar 1 — model field rebalance with explicit primary/fallback tiers and capability-based justification; Pillar 2 — new `scripts/check_*.py` static checker with same exit-code convention as existing tooling and KNOWN_X allowlists; Pillar 3 — doc governance (CHANGELOG extraction by content match, new R-rule in architecture, tool-tier index for single-source authority agents). Each task touches multiple files but stays in one wave per pillar; baseline diff via `git stash` before claiming \"no regression\". Agent fleet 治理升级, 模型分流, 廉价模型路由, primary fallback 分档, 静态校验脚本, 委派图检查, model allowlist, CHANGELOG 外移, 架构文档治理, R-rule 新增, 单源工具分层表, baseline regression diff."
revision: 1
---

# Agent Fleet Governance Update

> Crystallized from: agent-architecture-optimization (4 phases, 8 tasks) — DeepSeek V4 Pro routing for 8 agents + new `check_agent_delegation_graph.py` + CHANGELOG extraction + R7 cap policy + Format Engineer T1/T2/T3 quick reference
> Date: 2026-04-28
> Trigger: T3 (user explicit confirmation: "将...固化为 SKILL.md")

## When to Use

- A **new model tier** (cheaper or specialized) becomes available and the fleet should be rebalanced — typically a low-judgment-density tier (e.g. DeepSeek V4 Pro) for specialists whose workflows are ≥80% deterministic tool-call pipelines.
- A **new static governance check** is missing — e.g. delegation cycle detection, max-depth audit, agent count cap enforcement, model allowlist validation.
- The architecture doc has accumulated **≥4 inline version history blocks** that create diff noise on every minor revision and should be extracted to a CHANGELOG.
- A **single-source authority agent** (e.g. Format Engineer for formatforge T3, Literature Manager for Zotero writes) needs a quick-reference tool-tier table to clarify which tools other agents may hold directly vs must delegate.
- The combined work spans all three pillars (model + script + docs) — if only one pillar applies, prefer the narrower skills below.

## When NOT to Use

- Pure boundary clarification or single-tool-family centralization → use [`agent-fleet-boundary-cleanup`](../agent-fleet-boundary-cleanup/SKILL.md).
- Pure tool-budget trimming for the 128-tool cap → use [`agent-tool-budget-trim`](../agent-tool-budget-trim/SKILL.md).
- Single-agent iterative refinement from numbered user feedback → use [`agent-iterative-refinement`](../agent-iterative-refinement/SKILL.md).
- Brand-new agent authoring → use the `agent-customization` built-in skill.
- Rolling out an architecture spec section into mixed file types without a model/script change → use [`arch-spec-multi-file-rollout`](../arch-spec-multi-file-rollout/SKILL.md).
- Adding a runtime workflow check (executes during agent invocation) — this skill covers static checks only.

## Workflow

### Phase 0 — Audit (read-only)

1. Inventory current `model:` fields: `grep "^model:" *.md` — sort by primary model, identify candidates for rerouting.
2. Classify each agent into one of three judgment-density bands:
   - **Band A — high judgment**: keep premium model (Opus/GPT-Codex). Examples: Academic Writer, Paper Reviewer, Critical Thinking, Plan Architect.
   - **Band B — code/numerical**: keep GPT-Codex. Examples: Task Executor, Simulation Builder/Analyst, Data Analyst.
   - **Band C — deterministic/mechanical**: candidate for new tier. Examples: Citation Scanner (DOI cross-validation), Format Engineer (tool-chaining), Literature Manager (CRUD), Standards Navigator (long-context retrieval).
3. Within Band C, sub-classify into **primary** (≥80% deterministic, no creative judgment) vs **fallback** (has judgment component but new tier acceptable as degraded path).
4. Audit existing scripts under `scripts/` to identify the convention (exit codes 0/1/2, no-deps Python 3.8+ stdlib parsing, allowlist-style allowlists).
5. Audit architecture doc for inline version history blocks (`grep "^> \\*\\*v" docs/<arch>.md`) — extraction candidate if ≥4.
6. Output the audit table to user. **Do NOT modify files yet.**

### Phase 1 — Plan (Plan Architect, with Red-Team)

1. Draft a 4-phase plan: Phase 1 (model rebalance, multiple parallel tasks) → Phase 2 (new script) → Phase 3 (doc governance, sequential — extraction before doc additions) → Phase 4 (validation regression).
2. Document the **routing classification criterion** explicitly in the technical-design section. Without this, the plan looks like ad-hoc grouping. Red-Team will catch its absence.
3. Run `Critical Thinking` Red-Team review with 3 lenses (prompt injection / silent failure / cross-task drift). Pay particular attention to:
   - Single-model agents (no fallback) being swapped to a new model — must keep original as fallback.
   - Cross-model-family delegation chains (e.g. parent on Opus → sub-agent on DeepSeek) — flag for smoke test.
   - Hardcoded line numbers in extraction tasks — convert to content-match (`grep "^> \\*\\*v"`).
4. Address every High/Medium finding before finalizing the plan.
5. Establish an **Execution Wave** table: which tasks can parallel, which sequential.

### Phase 2 — Pillar 1: Model rebalance (parallel tasks)

For each agent in scope, modify only the `model:` line:

- **Primary swap**: `["NewTier (copilot)", "<original-fallback>"]` — new tier first, original second model becomes fallback.
- **Append fallback**: `["<original-primary>", "<original-fallback>", "NewTier (copilot)"]` — new tier appended last.
- **Critical**: never reduce a single-element model list to another single-element list — always preserve at least one fallback path.

After each task:
1. `grep "^model:"` to verify exact string.
2. `python3 scripts/check_agent_tool_budget.py` to confirm no new WARN/FAIL.
3. Commit per task with `[Plan: <plan-name>] Task X.Y: <agent-list> — <new-tier> <primary|fallback>` and ✅-mark the plan.

### Phase 3 — Pillar 2: New static checker script

Build `scripts/check_<name>.py` following existing conventions:

1. **No third-party deps** — Python 3.8+ stdlib only. Reuse line-based YAML parsing pattern from `check_agent_tool_budget.py`; do not introduce PyYAML.
2. **Exit codes**: 0 = OK, 1 = WARN, 2 = FAIL. Match `check_agent_tool_budget.py`.
3. **Configuration via constants near top** — `KNOWN_MODELS`, `BUILTIN_AGENTS`, `R6_ALLOWED_PAIRS`, etc. Maintainers update these when adding agents/models.
4. **CLI parameters via argparse** — anything that may need tuning (e.g. `--max-agents 32`, `--max-depth 10`, `--repo-root`) must be CLI-configurable, never hardcoded inside the function body.
5. **Realistic defaults** — when first run on the live fleet, the script should exit 0. If a default threshold immediately triggers a WARN on legitimate state (e.g. `--max-depth 4` but R2/R6/Dispatcher exceptions allow chains of 9), raise the default to the realistic value and document the tightening procedure in the help text.
6. **Self-test by injection**: write a synthetic 2-file repo to `/tmp/cycle-test/` with a fabricated cycle (or other failure pattern), run `python3 scripts/check_<name>.py --repo-root /tmp/cycle-test` and confirm exit 2. Clean up `/tmp/cycle-test/` after.
7. Commit with documentation of CLI parameters in the commit message.

### Phase 4 — Pillar 3: Documentation governance (sequential)

Tasks within this pillar must execute in strict order to avoid line-number drift:

1. **CHANGELOG extraction**: extract every `> **vX.Y 更新摘要**:` block from the architecture doc into `docs/CHANGELOG.md`. Use content-match patterns, NOT hardcoded line numbers. Replace the extracted region with a single line: `> 详细变更历史见 [CHANGELOG](CHANGELOG.md)`. Verify: `grep -c "^> \\*\\*v" docs/<arch>.md` returns 0 and `grep -c "^## v" docs/CHANGELOG.md` matches expected count.
2. **New R-rule in architecture**: append to the §2.2 rules table. Reference the new static checker script and its CLI parameters.
3. **Tool-tier quick reference**: insert a 3-row T1/T2/T3 table near the top of the single-source authority agent's design doc (e.g. `docs/format-engineer.md`). Each row lists scope + concrete tool names + holders. Keep it as an index — note "authoritative source is each agent's `tools:` field".
4. Commit each task separately.

### Phase 5 — Pillar 4: Validation regression with baseline diff

1. Run **all** existing validation scripts plus the new one:
   - `python3 scripts/check_agent_tool_budget.py`
   - `bash scripts/validate-portfolio.sh`
   - `python3 scripts/check_<name>.py` (new)
   - `bash scripts/verify-audit-rollout.sh`
   - `bash scripts/verify-deaifier-rollout.sh`
2. **Critical**: when a script exits non-zero, do NOT assume regression. Establish a baseline:
   ```
   git stash
   bash scripts/verify-X.sh > /tmp/X_pre.txt 2>&1; echo "pre-exit=$?"
   git stash pop
   bash scripts/verify-X.sh > /tmp/X_post.txt 2>&1; echo "post-exit=$?"
   diff /tmp/X_pre.txt /tmp/X_post.txt
   ```
   If pre and post counts match (or post is improved), document as **pre-existing tech debt, no regression introduced**.
3. **Smoke tests** for cross-model-family delegations (parent agent on Opus → sub-agent on new tier): mark as **user-side verification recommended** if MCP servers are not invocable in the current session. Do not block delivery on user-driven smoke tests.
4. Commit the regression report and ✅-mark the final task.

## Inputs & Outputs

| Input | Source |
|-------|--------|
| Audit of current `model:` fields | `grep "^model:" *.md` |
| Existing script conventions | `scripts/check_agent_tool_budget.py`, `scripts/validate-portfolio.sh` |
| Architecture doc with version history | `docs/<arch>.md` lines starting `> **vX.Y` |
| Single-source authority agent's tool list | `<agent>.md` `tools:` field |
| Pre-change baseline (for regression diff) | `git stash` → run validators → `git stash pop` |

| Output | Format |
|--------|--------|
| Updated `model:` fields in 8 agents | `*.md` frontmatter list, primary or fallback ordering |
| New static checker | `scripts/check_<name>.py`, exit codes 0/1/2, argparse CLI |
| New `docs/CHANGELOG.md` | One H2 per version: `## vX.Y` + bullet summary |
| Trimmed architecture doc | Inline version history removed; one-line CHANGELOG link added |
| New R-rule | Appended to §2.2 rules table with cap value + script reference |
| Tool-tier quick reference | 3-row Markdown table in single-source agent's design doc |
| Validation regression report | Per-script exit codes + baseline diff for non-zero exits |
| Per-task commits | `[Plan: <plan-name>] Task X.Y: <action>` |

## Common Pitfalls

- **Single-element model list dropped**: Citation Scanner had `model: ["GPT-5.3-Codex"]`. Naively replacing with `["DeepSeek V4 Pro"]` removes the only fallback. Always keep ≥2 elements after a primary swap.
- **Hardcoded line numbers in extraction tasks**: line 7–48 today is line 9–50 tomorrow if anyone tweaks the header. Use content-match (`grep "^> \\*\\*v"`) and `replace_string_in_file` with the full block as `oldString`.
- **Unrealistic default thresholds in new checker**: `--max-depth 4` sounds principled but R2/R6/Dispatcher exceptions allow chains of 9 (FDR → PA → TE → AW → PR → DC → CV → SPR → LM → Explore). Default to a realistic value (10) so first-run is exit 0; let auditors tighten via CLI.
- **`set -e` in test commands hides script exit codes**: when running validation in a chained command, capture exit immediately: `bash scripts/X.sh > /tmp/X.txt 2>&1; rc=$?; echo "exit=$rc"`. Don't pipe through `tail` before capturing `$?`.
- **`git stash`/`git stash pop` round-trip**: always verify state with `git stash list` (empty) and `git status -s` (clean) afterward. A leftover stash can silently shadow your changes.
- **Mid-extraction `git checkout <hash>`** for baseline comparison detaches HEAD and untracks all subsequent edits — prefer `git stash` (lightweight) over `git checkout <hash>`. If detached HEAD happens, `git checkout main` then `git checkout main -- .` to restore.
- **Cross-model-family delegation untested**: Doublecheck (Opus) → Citation Scanner (DeepSeek V4 Pro) crosses model families mid-pipeline. The parent's prompt formatting may not match sub-agent's interpretation. Schedule end-to-end smoke test even if it must be user-side.
- **R-rule references the new script** but the new script is built later: ensure Phase 2 (script) commits before Phase 3 (R-rule). Wave ordering matters.
- **Smoke tests blocking delivery**: MCP-dependent end-to-end tests should be marked as user-side verification recommended, not as blocking failures, when the current session cannot invoke the MCP servers.
- **`grep -c "T1\|T2\|T3"` returning 3** sounds like a meaningful test but matches any prose mentioning the strings. Check the table structure exists with a more specific pattern (e.g. `grep "^| \*\*T1"`) for stronger validation.

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-04-28 | Initial crystallization | agent-architecture-optimization plan: 4 phases, 8 tasks, commits 5bcd334..9a1e598 — 8 model field updates + new `check_agent_delegation_graph.py` + CHANGELOG extraction + R7 + FE T1/T2/T3 table |
