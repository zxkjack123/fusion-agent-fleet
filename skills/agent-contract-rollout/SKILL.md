---
name: "agent-contract-rollout"
description: "Add structured inbound `## 委派合同` contracts or outbound `## Outbound Delegation Schemas` to agent files in bulk, with paired portfolio/audit validation gates and per-task commits. 批量为 agent 文件添加入站委派合同/出站委派 schema, 配套校验门禁, 每任务独立提交. agent IO schema, delegation contract, agent.md inbound outbound, validate-portfolio, verify-audit-rollout, check_delegation_contracts."
revision: 1
---

# Agent Contract Rollout

> Crystallized from: agent-io-schema-rollout-p0p2 plan execution (32 tasks)
> Date: 2026-05-24
> Trigger: T3 (user-confirmed)

## When to Use

- Rolling out a Plan Architect plan that adds structured `## 委派合同` (inbound) or `## Outbound Delegation Schemas` (outbound) sections to multiple `*.md` files in the copilot-agents repo.
- Adding a new structured-IO section to a single agent following an existing plan's per-task format.
- Filling out `[contract: pending — ...]` placeholder markers by replacing them with `(see <callee>.md → ### 调用方需提供)` references once the callee has published its inbound contract.

## When NOT to Use

- Rewriting an agent's prose body (use Repo Reviewer / Plan Architect to redesign instead).
- Adding/removing tools, agents, or applyTo entries in frontmatter (different surface, different validators).
- Touching files outside `*.md` at workspace root (e.g., `.github/agents/*`, `agent-workflows/`).
- Bulk-edit operations that should be a single commit — this skill enforces per-task commits.

## Workflow

For each task in the plan, repeat exactly this sequence:

1. **Locate anchor**: `grep -nE '^revision:|^## ' <name>.md` to find current `revision: N` line and the section after which the new block will be appended (typically end of file).
2. **Append the contract block** with a heredoc:
   - **Inbound**: `## 委派合同 — Mandatory Structured Report` → `### 调用方需提供` (bullets `- field (type, required/optional[, default]): description`) → `### Final Report 强制格式` pointing to an existing delivery section (e.g. `## Final Report`, `## Output Format`).
   - **Outbound**: `## Outbound Delegation Schemas` (with the italic disclaimer line) → one `### CalleeName` subsection per callee containing `**When to delegate**:`, `**Required prompt fields** (see \`<callee>.md\` → \`### 调用方需提供\`):` followed by field bullets.
3. **Bump revision**: `sed -i "s/^revision: N$/revision: $((N+1))/" <name>.md`.
4. **Run validation gates** (all must pass before commit):
   - `bash scripts/validate-portfolio.sh 2>&1 | tail -2` → expect `✅ Portfolio validation PASSED`.
   - `bash scripts/verify-audit-rollout.sh 2>&1 | tail -3` → expect `PASS: 98 | FAIL: 0 | SKIP: 42` (numbers may evolve; lock to current baseline at plan start).
   - **Outbound only**: `python3 scripts/check_delegation_contracts.py 2>&1 | tail -3` → expect exit 0, ref count increases by N (one per `(see ...)` reference added).
5. **Mark plan checkbox**: in `.github/plans/<plan>.md` replace `#### Task X.Y:` → `#### ✅ Task X.Y:` via `replace_string_in_file`.
6. **Commit**:
   ```
   git add <name>.md .github/plans/<plan>.md
   git commit -m "[Plan: <plan-name>] Task X.Y: <short title>

   - <bullet of what changed>
   - Bump revision N → N+1
   - [PM: skipped]"
   ```
   Never run `git push`.
7. **Report progress**: `✓ Task X.Y done [k/total]`.

For the final cleanup task (replacing `[contract: pending — ...]` markers):

- Use `multi_replace_string_in_file` to swap all occurrences with `(see \`<callee>.md\` → \`### 调用方需提供\`)`.
- Bump revision on every file touched.
- Run all three gates; expect `check_delegation_contracts` ref count to jump by the number of markers cleared.
- Single commit for the whole cleanup task.

## Inputs & Outputs

| Input | Source |
|-------|--------|
| Plan file with 1.0+ schema and per-task field-level spec | `.github/plans/<plan-name>.md` |
| Existing agent files to be modified | `<repo-root>/*.md` |
| Callee inbound contract location (for outbound refs) | Target file's `### 调用方需提供` heading |

| Output | Format |
|--------|--------|
| Modified agent file with new structured section + bumped revision | `<name>.md` |
| Plan file with `#### Task` → `#### ✅ Task` checkboxes | `.github/plans/<plan>.md` |
| One git commit per plan task | branch (e.g. `test/<round>`), never pushed |

## Common Pitfalls

- **Pre-commit Check 3 false-positive on `### Stage X: ...` backticks**: never write a backtick-wrapped `` `### Stage A: ...` `` in agent body prose; the audit regex `### Stage ([A-Z])(?=[\s:—])` misreads it as a real heading. Use `Stage X (Description)` form instead.
- **Forgetting the revision bump**: portfolio validator does not fail on stale revision, but reviewer expects monotonic increase. Always `sed -i "s/^revision: N$/revision: N+1/"` after each content change.
- **Wrong Final Report anchor**: inbound block's `### Final Report 强制格式` must point to a section that already exists in the file (e.g. `## Final Report`, `## Output Format`, `## Output Format Rules`). Grep first; do not invent.
- **`check_delegation_contracts.py` only matters for outbound tasks**: skipping it on inbound-only tasks is fine, but every outbound commit must bump its PASS count.
- **`[PM: skipped]` footer is mandatory** per project-management-mcp instruction's MCP-unavailable fallback policy. Include it in every commit body.
- **Never `git push`**: per career-strategy + operationalSafety guidance, this rollout runs entirely on a local branch.
- **Don't batch commits**: one task = one commit. The plan's audit trail and rollback depend on per-task granularity.

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-05-24 | Initial crystallization | agent-io-schema-rollout-p0p2 (32 tasks, 32 commits, all gates green) |
