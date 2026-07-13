---
name: "agent-tool-budget-trim"
description: "Audit and trim OpenCode agent tools: declarations to stay under the 128-tool hard cap (microsoft/vscode#290356). Inventory every MCP server's real tool count, build a per-server allow-list when wildcards are too costly, and validate via a static budget script — preventing virtual-tools from silently disabling fine-grained tools like remote_ls/remote_find. 防止 OpenCode agent 工具数超 128 上限触发 virtual tools 静默丢弃, MCP server 工具清单收集, allow-list 替换 wildcard, 预算脚本静态校验, frontmatter tools 块裁剪."
revision: 1
---

# Agent Tool Budget Trim

> Crystallized from: copilot-agents repo, plan `agent-tool-budget-trim` (11 tasks across discovery → pilot → rollout → guardrails). 23 agents originally used `server/*` wildcards; 7 were FAIL (>80 estimated tools), 2 of which (`task-executor`, `fusion-deep-research`) exceeded 200. Triggered by user-visible failure: `The MCP tools remote_ls and remote_find are disabled in your session`.
> Date: 2026-04-23
> Trigger: T1 (≥5 distinct tool steps; 11 sequential tasks executed)

## When to Use

- A chat session reports `Tool limit exceeded (N/128)`, or specific MCP tools (often the long-tail ones like `remote_ls`, `remote_find`, `remote_grep`) appear "disabled in your session" without clear cause.
- An audit (e.g., Repo Reviewer) finds multiple `*.md` files use ≥6 `server/*` wildcards each, or any single agent declares ≥10 MCP wildcards.
- Adding a new MCP server to an existing heavy agent and you want to confirm it still fits the 128-tool budget before commit.
- Onboarding a new fleet of agents into a workspace where the global tool catalog is unknown.

## When NOT to Use

- Agents declare ≤5 MCP wildcards total — wildcards are still optimal at small scale; do not over-engineer.
- The reported failure is `Tool not available` for a tool that is **not** declared in `tools:` (that is a missing-permission bug, not a budget bug).
- The fix would require modifying an MCP server's source code (forbidden by `mcp-usage-policy.instructions.md`). Tool-budget trimming only edits agent frontmatter.
- The user wants to add **new capability**, not preserve existing capability — capability changes go through `agent-iterative-refinement` instead.

## Workflow

### Phase 1: Discovery

1. **Triage with a one-liner**: count MCP wildcards per agent to find candidates.
   ```bash
   for f in *.md; do
     n=$(awk '/^tools:/{flag=1;next} flag && /^[a-zA-Z]/{flag=0} flag' "$f" | grep -cE '/\*$')
     printf "%-32s wildcards=%s\n" "$f" "$n"
   done | sort -k2 -t= -rn
   ```
   Anything with ≥6 wildcards is a likely FAIL once expanded.

2. **Build/refresh `scripts/mcp_tool_inventory.json`** with one entry per MCP server:
   - Preferred source: `instructions/<server>*.instructions.md` if it enumerates tools in a table.
   - Fallback source: query the live chat session (`<server>/tool_list` or function-catalog introspection) and paste the names.
   - Conservative fallback: `"tools": "unknown"` + `"estimate_upper_bound": <N>` (default 10).
   - Always add `"source"` and `"_note"` fields so future readers can audit the data.
   - For heavy servers like `scnetresource-router`, also define a `core_allowlist` field — the canonical 10–20 tools the workflow actually needs.

3. **Write/refresh `scripts/check_agent_tool_budget.py`** (pure stdlib):
   - Parse YAML `tools:` block per agent (regex on `^tools:` until next top-level key).
   - Classify entries: `builtin` (use `BUILTIN_GROUP_WEIGHT` table, ~1–4 tools each), `mcp_wildcard` (lookup inventory length), `mcp_explicit` (count = 1).
   - Output TSV table with `est_total` and `status` (OK ≤60 / WARN 60–80 / FAIL >80).
   - Exit codes 0/1/2 for CI integration.

### Phase 2: Pilot

4. Pick the **single highest-FAIL agent** (typically `task-executor` or the orchestrator) as pilot.
5. **Audit body usage** to know which servers are real dependencies:
   ```bash
   BODY_LINE=$(awk '/^---$/{n++; if(n==2){print NR; exit}}' <agent>.md)
   tail -n +$((BODY_LINE+1)) <agent>.md > /tmp/body.md
   for srv in <list_of_servers>; do
     refs=$(grep -cE "${srv}|<known_tool_prefix>" /tmp/body.md)
     [ "$refs" -gt 0 ] && printf "%-25s %s\n" "$srv" "$refs"
   done
   ```
   Note: also grep for tool prefixes that are not the server name (e.g., `pm_*` for `project-management`, `memory_*` for `session-memory`).

6. **Capture body bytes BEFORE editing**: `tail -n +$((BODY_LINE+1)) <agent>.md | wc -c > /tmp/<agent>_body_before.txt`. This is the regression check that proves the body stayed untouched.

7. **Rewrite frontmatter `tools:` block** with a single `multi_replace_string_in_file` using a strict `oldString` ↔ `newString` swap. Apply this decision tree per server:
   - Inventory size ≤5 → keep `server/*` wildcard.
   - Body has zero references → drop entirely.
   - Body uses ≥1 tool, inventory >5 → expand to explicit `server/<tool>` lines covering every body reference (verify with `comm -23`).
   - Always bump `revision` by 1 in the same edit.

8. **Verify body bytes unchanged**: `tail -n +$((NEW_BODY_LINE+1)) <agent>.md | wc -c` must equal the captured pre-edit value. If different, the edit accidentally touched the body — abort and retry.

9. **Re-run the budget script** and grep for the pilot agent — must show non-FAIL.

10. **Live smoke test (user collaboration)**: write a runbook to `.github/plans/<plan>.smoke-test.md` instructing the user to reload VS Code and trigger the previously-disabled tool. The static budget cannot fully predict virtual-tools grouping; only a real chat session confirms.

### Phase 3: Rollout

11. Apply Phase 2 steps 5–9 to remaining FAIL/WARN agents, in descending estimated-total order. Use `multi_replace_string_in_file` to batch 2–3 agents per commit when the change is mechanical and identical.

12. For orchestrator agents (those with a populated `agents:` delegation list), prefer to **drop wildcards for specialty servers that a subagent owns** (e.g., orchestrator drops `tikz-writer/*` because it delegates to a Diagram Architect that holds the wildcard). Subagents have independent budgets.

### Phase 4: Guardrails

13. Write `docs/tool-budget.md` (≥50 lines) covering: cap facts with source link, virtual-tools failure modes, decision tree, script usage, new-server onboarding, common mistakes.

14. Add a `## Tool Budget` section to `README.md` linking the docs and the script.

15. Append the final `python3 scripts/check_agent_tool_budget.py` output to the plan's "完成情况" section. Use `python3 ... >> file` redirection — do **not** pipe through `cat <<EOF` heredocs because tab characters in the TSV get mangled.

## Inputs & Outputs

| Input | Source |
|-------|--------|
| All `*.md` at repo root | Workspace root |
| Existing `instructions/<server>*.instructions.md` files (for tool name discovery) | `instructions/` |
| Live MCP function catalog (for unknown servers) | Current chat session |
| Original Repo Reviewer report (recommended trigger) | `.github/reviews/` |

| Output | Format |
|--------|--------|
| Tool inventory data | `scripts/mcp_tool_inventory.json` |
| Budget check script | `scripts/check_agent_tool_budget.py` (executable, pure stdlib) |
| Trimmed agent frontmatters | `<agent>.md` (frontmatter only; body byte-identical; `revision` +1) |
| Author guide | `docs/tool-budget.md` |
| README cross-link | `README.md` (new `## Tool Budget` section) |
| Per-task commits | `[Plan: agent-tool-budget-trim] Task X.Y: ...` |
| Smoke-test runbook | `.github/plans/<plan>.smoke-test.md` |

## Common Pitfalls

- **Trusting the static budget alone.** The 128-cap mitigation (virtual tools) is embedding-driven and can silently fold tools into umbrella surrogates even when est_total is 47. Always pair the static check with a live chat smoke test for at least one pilot agent.
- **Forgetting tool-prefix grep.** When auditing body usage, grepping only for `server-name` misses references like `pm_task_create` (server `project-management`) or `memory_recall` (server `session-memory`). Include both forms: `grep -cE "${srv}|<prefix>_"`.
- **Heredoc-mangling tab characters.** Appending TSV output via `cat <<EOF` collapses tabs and corrupts the table. Use `python3 script.py >> file` direct redirection instead.
- **Over-trimming the orchestrator before subagents are ready.** Dropping `tikz-writer/*` from the orchestrator only works if the user actually delegates to the Diagram Architect subagent. If their typical workflow is direct invocation, this breaks them. Confirm the delegation pattern in the orchestrator's body before trimming.
- **Forgetting `revision` bump.** Tool-surface changes are invisible in `git log` without it; reviewers cannot tell that the agent's capabilities changed.
- **Editing the agent body to "fix" budget overflow.** Wrong target — only the frontmatter `tools:` block affects the catalog size. The body byte-count check is the safety net.
- **Counting built-in groups as 1 tool each.** They actually expand to several underlying tools (read=2, edit=4, search=4, etc.). The budget script's `BUILTIN_GROUP_WEIGHT` table encodes this; do not bypass it.
- **Forgetting unknown-server warnings.** When the inventory has no entry for a wildcard, the script counts it as 10 and warns to stderr. Suppressing stderr (`2>/dev/null`) hides this signal — only do so for human-readable summary, not for CI.
- **Auto-pushing.** Per workflow rules, never `git push` automatically. Stop at commits.

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-04-23 | Initial crystallization | copilot-agents plan `agent-tool-budget-trim` (11 tasks; trimmed 7 high-risk agents from FAIL to ≤WARN; introduced budget script + author guide) |
