---
name: "agent-iterative-refinement"
description: "Iterative refinement of a single agent definition file (*.md) based on real-world usage feedback. Plan-Architect drafts numbered improvement tasks (A1, A2, ...), Task-Executor applies one-edit-per-task with grep-based acceptance tests and per-task commits, then bumps the design doc changelog. Agent 文件迭代改进, 真实使用反馈驱动的小步多轮改动, 编号任务 + 每任务独立 commit + changelog 同步."
revision: 1
---

# Agent Iterative Refinement

> Crystallized from: presentation-architect v0.5.0 (7 tasks) + v0.6.0 (7 tasks) — both rounds applied 6+ scattered improvements to a single `*.md` based on user-observed runtime issues.
> Date: 2026-04-19
> Trigger: T1 (≥5 distinct tool-call steps) + T2 (≥2 occurrences with consistent tool chain)

## When to Use

- User reports a list of distinct, numbered improvement points (A1, A2, ... or 1, 2, ...) for a single existing `*.md` after observing it in real use.
- Each improvement is bounded (touches 1–3 sections of the agent file) and does not require new MCP tools or new architectural concepts.
- The agent has a `docs/<agent-name>.md` design doc with a `## Changelog` section (versioned v0.x.y).
- Improvements naturally map to "insert clause", "rewrite step", "renumber section", "append note" — not whole-stage redesigns.

## When NOT to Use

- Adding a brand-new MCP server or tool to the agent's `tools:` front-matter (that's a capability change, not refinement).
- Cross-agent restructuring (multiple `*.md` files affected) — use a dedicated comparison/audit plan instead.
- Improvement requires changing the underlying MCP server's source code or schema (forbidden by `mcp-usage-policy.instructions.md`).
- The user wants a "complete rewrite" rather than localized edits.

## Workflow

### Phase A: Plan (Plan Architect)

1. Read the current `*.md` and corresponding `docs/<agent-name>.md` to anchor existing structure (stage list, step numbering, existing changelog version).
2. Map each user improvement point (A1, A2, ...) to:
   - Target stage / step number to modify (or new step to insert)
   - Whether numbering shift is required (and the renumbering range)
   - Reused existing pattern (e.g., another step's "detect → log → user decision" template)
3. Group tasks into 2–3 phases by stage locality (e.g., "Phase 1: Stage D", "Phase 2: Stage D.5", "Phase 3: Stage E + docs").
4. Write the plan to `.github/plans/<agent-name>-v<x.y.z>-improvements.md`. Each task must include:
   - **目标** / **修改内容** / **修改边界** (forbidden modifications) / **测试要求** (grep commands with expected output) / **验收标准** (binary checks) / **潜在风险** (with mitigation)
5. Add a regression checklist covering numbering continuity (`grep -cE "^[0-9]+\. "` per stage), preserved cross-references, and unchanged tool-inventory tables.
6. Run 3 rounds of internal self-review (R1 structure, R2 executability, R3 risk) and append the audit log.

### Phase B: Execute (Task Executor)

For each task, in order:

1. **Read** the target stage to confirm exact text (don't trust memory across tasks).
2. **Edit** using `replace_string_in_file` (single edit) or `multi_replace_string_in_file` (multiple edits for renumbering).
3. **Test** via grep commands defined in the task's "测试要求" section. Verify:
   - New keyword/clause is present
   - Numbering is continuous (e.g., `awk '/^### Stage X/,/^### Stage Y/' file | grep -cE "^[0-9]+\. "`)
   - Preserved sections unchanged (e.g., `grep -c "Template fallback detection" file` returns 1)
4. **Mark plan**: change `#### Task X.Y:` to `#### ✅ Task X.Y:` in the plan file.
5. **Commit** with message format: `[Plan: <plan-name>] Task X.Y: <one-line summary>` + bullet list of changes + `All acceptance criteria passed`.

### Phase C: Finalize

1. Run full regression checklist from the plan (numbering continuity, preserved refs, MCP tool inventory row count unchanged).
2. Output completion summary with commit hashes per task and instruction `git push` (do NOT auto-push).
3. Run skill-crystallization detection (T1/T2/T3) for the next iteration.

## Inputs & Outputs

| Input | Source |
|-------|--------|
| Current `*.md` | Workspace root |
| Design doc `docs/<agent-name>.md` (with `## Changelog`) | `docs/` |
| User improvement list (numbered A1...AN or 1...N) | User message |
| Previous version's plan file (for naming convention) | `.github/plans/` |

| Output | Format |
|--------|--------|
| Plan file | `.github/plans/<agent-name>-v<x.y.z>-improvements.md` |
| Updated agent file | `<agent-name>.md` |
| Updated design doc | `docs/<agent-name>.md` (new changelog entry above the previous version) |
| Per-task git commits | `[Plan: <plan-name>] Task X.Y: ...` |

## Common Pitfalls

- **Renumbering breaks internal cross-references.** When inserting a new numbered step in the middle of a stage, grep for `step [N+1]`, `Stage X step N`, and `mapping table in step N` patterns elsewhere in the file. Update them in the same task.
- **Cumulative renumbering across tasks.** If Task 1.2 inserts a step into Stage D and Task 2.3 inserts a step into Stage D.5, do NOT plan both renumberings against the original baseline — re-read the file at the start of each task to see the current numbering.
- **Grep with backticks in command line fails on em-dash / unicode.** Use `awk` range slicing first, then plain `grep -c`. Avoid putting unicode chars (✅ ⚠️ ℹ️) inside the grep regex.
- **Missing changelog entry.** The design doc changelog is the audit trail; forgetting it makes the version bump invisible. Always make the changelog update its own task in Phase 3.
- **MCP tool inventory drift.** If the refinement claims "no new tools added", verify by counting table rows before and after (`awk '/^## .* MCP Tool Inventory/,/^## /' file | grep -cE "^\| "` should be unchanged).
- **Over-engineering the user's request.** The user already wrote down A1–A6 — implement exactly those, do not add A7 "while we're here".
- **Auto-pushing.** Per `workflow_preferences.md`, never `git push` automatically. Stop at commits.
- **Confusing version-bump scope.** Use `v0.X.0` for ≥3 user-facing changes (this skill's typical scope); reserve `v0.X.Y` patches for single-point fixes.

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-04-19 | Initial crystallization | presentation-architect v0.5.0 + v0.6.0 (2 rounds, 7+7 tasks, A1–A6 pattern) |
