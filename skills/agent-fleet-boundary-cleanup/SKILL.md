---
name: "agent-fleet-boundary-cleanup"
description: "Fleet-wide agent role-boundary clarification and tool authority tiering. Use when multiple *.md files have overlapping roles, ambiguous boundaries, or scattered tool ownership of complex pipelines (e.g. document conversion, simulation submission). Audit -> prioritize (P0/P1/P2/P3) -> plan -> wave-based execution: add Boundary statements to descriptions, tier tools (T1 ingestion / T2 last-mile / T3 complex pipeline), centralize T3 tools in a single-source authority agent, bump revisions, validate via budget script. Agent fleet 工具权限分层治理, 角色边界澄清, T1/T2/T3 工具分级, single-source authority, budget 校验."
revision: 1
---

# Agent Fleet Boundary & Tool-Tier Cleanup

> Crystallized from: agent-clarity-boundary-cleanup plan (4 phases, 13 tasks) — boundary statements + T3 tool authority enforcement across 25-agent fleet
> Date: 2026-04-25
> Trigger: T3 (user explicit confirmation after near-certain pattern recurrence)

## When to Use

- Fleet has ≥10 agents and several pairs/triples appear functionally overlapping (e.g. critical-thinking vs doublecheck, paper-reviewer vs innovation-reviewer).
- The same complex tool family (formatforge T3 ops, scnetresource HPC ops, etc.) is wired into many agents instead of being delegated to a single authority.
- Agent budget script reports WARN/FAIL on multiple agents because of tool-list bloat.
- User explicitly asks to "clarify roles", "fix boundaries", "centralize X tools", or "audit fleet".
- Stale tool references (e.g. ai-ppt/list_templates, deprecated MCP tools) are scattered across agent files.

## When NOT to Use

- Single-agent refinement based on numbered user feedback → use `agent-iterative-refinement` instead.
- Pure budget trimming without role-boundary issues → use `agent-tool-budget-trim` instead.
- Drafting a brand-new agent from scratch → use the `agent-customization` skill.
- The fleet is small (<5 agents) and overlap is obvious; direct edit is cheaper than a planned cleanup.

## Workflow

### Phase 0 — Audit (read-only)

1. List all `*.md` files at fleet root; for each read the frontmatter (name, description, tools).
2. Run the budget script: `python3 scripts/check_agent_tool_budget.py` — record current per-agent budget.
3. Identify three categories of issues:
   - **Boundary ambiguity**: descriptions of agents A and B overlap; users can't tell which to invoke.
   - **Tool authority dispersion**: complex tool family X appears in N≥3 agents.
   - **Stale references**: tools that no longer exist or have been deprecated upstream.
4. Output an audit table to the user. Do NOT modify files yet.

### Phase 1 — Prioritization recommendation

1. Group findings into priorities:
   - **P0** (no risk, immediate): description-only edits (Boundary statements, stale-tool removal).
   - **P1** (medium risk): adjustments to a single high-budget agent (e.g. FDR body cleanup).
   - **P2** (cross-cutting): tool authority recovery — remove T3 tools from many agents, centralize in one authority.
   - **P3** (cosmetic / nice-to-have): description refinement of the authority agent itself.
2. Recommend execution order: P0 + P3 (no risk) → P1 → P2 (highest blast radius last).
3. Ask user to confirm before drafting the detailed plan.

### Phase 2 — Plan drafting

1. Write a plan file under `.github/plans/<plan-name>.md` with waves matching priority order:
   - Wave 1 (P0): Boundary statements + stale-tool cleanup.
   - Wave 2 (P1): Single-agent body cleanup (if needed).
   - Wave 3 (P2): T3 tool authority recovery (remove from many, add authority agent to `agents:` list).
   - Wave 4 (P3): Authority-agent description refinement.
   - Wave 5: Final cross-validation.
2. For each task specify: target files, exact modifications, acceptance criteria, expected revision bumps, expected budget delta.
3. Define the **tool tier model** explicitly:
   - **T1 Ingestion**: any agent may hold (e.g. `pdf2md/*`, `convert_docx_to_markdown`, `wps_detect`).
   - **T2 Last-mile**: any producer may hold (e.g. `convert_markdown_to_docx`, `lint_markdown`).
   - **T3 Complex pipeline**: ONLY the authority agent (e.g. `publish_*`, `refs_*`, `validate_*`, `wps_fix`, `template_*`).

### Phase 3 — Wave execution (one wave at a time, commit per wave)

1. **Wave 1 (P0)**: For each agent needing a boundary statement, append `Boundary vs <other-agent>: ...` to the description. Bump revision. Remove stale tool refs from frontmatter AND body. Commit.
2. **Wave 2 (P1)**: Body cleanup only — re-section, remove dead text, align terminology. Bump revision. Commit.
3. **Wave 3 (P2)**: For each non-authority agent that holds T3 tools:
   - Remove T3 tools from the `tools:` block (frontmatter).
   - Pre-check the body for any references to those removed tools and rewrite them as "delegate to <authority>".
   - Add the authority agent's name to the `agents:` list.
   - Bump revision.
   - Run budget script — confirm no FAIL.
4. **Wave 4 (P3)**: Refine the authority agent's description to explicitly state the T1/T2/T3 tier model and "single-source authority for T3". Bump revision. Commit.
5. **Wave 5**: Cross-validation (see Phase 4).

### Phase 4 — Cross-validation (required before final delivery)

Run all four checks:
1. Budget: `python3 scripts/check_agent_tool_budget.py 2>&1 | awk '$NF=="FAIL"'` → must be empty.
2. T3 tool ownership: `grep -l '<T3-tool-name>' *.md` → must be ONLY the authority agent.
3. Boundary count: `grep '^description' *.md | grep -c 'Boundary vs'` → must equal target from plan.
4. Authority delegation count: `grep -l '<Authority Agent Name>' *.md | wc -l` → must equal expected fleet coverage.

## Inputs & Outputs

| Input | Source |
|-------|--------|
| User audit/cleanup request | Chat |
| Fleet agent files | `*.md` at workspace root |
| Budget script | `scripts/check_agent_tool_budget.py` |
| Tool tier definitions | `instructions/formatforge-tools.instructions.md` (or analog for other tool families) |

| Output | Format |
|--------|--------|
| Plan file | `.github/plans/<plan-name>.md` |
| Edited agent files | `*.md` with bumped revision, boundary statements, tiered tools, authority delegation |
| Per-wave commits | Conventional `[Plan: <name>] Tasks X.Y-X.Z: ...` |
| Final summary report | Markdown table of completed tasks + commits + validation results |

## Common Pitfalls

- **multi_replace pattern brittleness**: T3 tool removal patterns assumed `wps_fix\nmodel:` but actual files had `wps_fix\n  - ldr/...`. Always grep the file first to confirm the exact next-line content before composing the replacement pattern.
- **Body references to removed tools**: removing a tool from frontmatter alone leaves dangling references in the body's "Tool Inventory" / "Workflow" sections. Always grep the body for the tool name BEFORE removing from frontmatter, and rewrite those refs as "delegate to <authority>".
- **Forgetting `agents:` list update**: removing a T3 tool without adding the authority agent to `agents:` breaks the delegation contract — the agent loses both the tool and the way to call it.
- **Budget WARN is acceptable, FAIL is not**: a WARN (>60) on the authority agent (e.g. FDR=61) is expected and fine; only block on FAIL (>80) or hard cap (128).
- **Revision bump consistency**: every modified frontmatter must bump revision by exactly +1 per task affecting it. If two waves both modify the same agent, that's +2 total — easy to miss.
- **Committing too coarsely**: one giant commit covering all waves makes rollback painful. Commit per wave (or per phase) so each is independently revertable.
- **Skipping Phase 0 audit**: jumping straight to edits without an audit table risks missing whole classes of issues (e.g. stale tool refs that don't trigger boundary concerns).

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-04-25 | Initial crystallization | agent-clarity-boundary-cleanup plan: 4 phases, 13 tasks across 25-agent fleet; Boundary statements (6 agents), FDR body cleanup, T3 formatforge tool centralization in format-engineer (9 tools removed from FDR, 3 from academic-writer, wps_fix from 6 reviewers), FE description refined to T1/T2/T3 model |
