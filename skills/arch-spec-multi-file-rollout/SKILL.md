---
name: "arch-spec-multi-file-rollout"
description: "Multi-file rollout of an architecture/design markdown specification into the live codebase. Plan-Architect derives a small numbered task list (≤6 tasks across 1–2 phases) from a `docs/<arch>.md` spec section, touching mixed file types (`*.instructions.md` + `*.md` + new `docs/<index>.md` + audit task), each agent/instruction file gets its `revision:` bumped, all tasks committed individually with `[Plan: <plan-name>]` prefix. Architecture spec rollout, ecosystem prep, multi-file change, instruction + agent + index doc, 架构落地, 设计文档落地, 多文件改造, 生态准备, instruction 与 agent 同步更新, revision 递增."
revision: 1
---

# Architecture Spec Multi-File Rollout

> Crystallized from: openmc-repo-a-improvements (5 tasks across 4 files: 1 instruction + 2 agents + 1 new ecosystem index + 1 audit) — rolled out the OpenMC 3-repo architecture's §2.2 improvement items into Repo A as preparation for new Repo B/C.
> Date: 2026-04-26
> Trigger: T1 (≥5 distinct tool-call steps) + T3 (user explicit "结晶为 SKILL.md")

## When to Use

- A pre-existing architecture/design markdown document (e.g., `docs/<arch>.md`) contains an explicit list of improvement items that need to be rolled out into the live codebase.
- The rollout touches **multiple file types** in a coordinated way (typical mix: `*.instructions.md` + 1–3 `*.md` + a new `docs/<index>.md` + 1 audit task).
- Each file change is bounded and orthogonal — no cross-task data dependencies, all tasks parallelizable in the same wave.
- The new MCP tools / external repos referenced are **not yet deployed** — placeholder links (`(link TBD)`) and tool declarations are acceptable; the rollout prepares the ground without runtime hard dependencies.
- Total task count is small (≤6 tasks), execution time is short (single agent session).

## When NOT to Use

- The improvements are a numbered A1–AN list of refinements to a **single** `*.md` based on user feedback → use [`agent-iterative-refinement`](../agent-iterative-refinement/SKILL.md) instead.
- The rollout requires building/deploying new MCP servers or repos as part of the same plan → split into separate construction plans (those are larger, multi-phase efforts).
- The architecture document itself is being authored or revised → that's design work, not rollout.
- Cross-agent fleet-wide boundary cleanup (≥6 agents touched) → use [`agent-fleet-boundary-cleanup`](../agent-fleet-boundary-cleanup/SKILL.md) instead.
- The improvement items haven't been distilled into a discrete list yet — the architecture doc must already have a "what to do in Repo X" section.

## Workflow

### Phase A: Plan (Plan Architect)

1. Read the source architecture doc's improvement section (e.g., `docs/3-repo-architecture.md` §2.2). Anchor each item to a concrete file + edit location.
2. Read the current state of every target file to get exact `revision:` numbers and existing structure (stage list, frontmatter fields).
3. Group tasks into 2 phases by file type:
   - **Phase 1**: in-place modifications to existing instruction + agent files (revision bumps live here)
   - **Phase 2**: new index doc creation + audit task (no revision bumps)
4. Write the plan to `.github/plans/<arch-prefix>-<repo>-improvements.md`. Each task must include:
   - **目标** / **修改内容** (with exact YAML/markdown snippets) / **修改边界** (forbidden modifications) / **测试要求** (grep + YAML parse commands) / **验收标准** / **潜在风险**
5. Mark Repo B/C cross-references and external links as `(link TBD)` placeholders — never fabricate URLs.
6. Add Error & Rescue Map covering: missing-MCP-tool degradation, retry-exhaustion behavior, placeholder link policy.
7. Run R1/R1.5/R2/R3 self-review and append the audit log.

### Phase B: Execute (Task Executor)

For each task, in order:

1. **Read** the target file to confirm exact text and current `revision:` value.
2. **Edit**:
   - For instruction files: insert content between frontmatter `---` and the first `# H1` heading; bump `revision:` in frontmatter.
   - For agent files: use `multi_replace_string_in_file` to (a) bump `revision:`, (b) extend `tools:` block, (c) insert new Stage. All in one call.
   - For new index doc: `create_file` with full content based on architecture doc §7 template.
3. **Test** with the task-specific commands:
   - `grep -n` for new keywords in expected line ranges
   - `python3 -c "import yaml; ..."` to verify YAML frontmatter still parses
   - For new files: `test -f` + grep for placeholder markers (e.g., `(link TBD)`)
4. **Mark plan**: change `#### Task X.Y:` to `#### ✅ Task X.Y:` in the plan file.
5. **Commit** with format: `[Plan: <plan-name>] Task X.Y: <summary>` + bullet list of changes + `All acceptance criteria passed`. Stage both the modified target file(s) and the plan file in the same commit.

### Phase C: Finalize

1. Run regression checklist:
   - All `revision:` fields incremented (one per modified agent/instruction file)
   - All YAML frontmatter still parses
   - No fabricated URLs (`grep -c "link TBD"` ≥ expected count for new index doc)
   - No runtime hard-dependency on undeployed repos (target files still load when MCP server absent)
2. Output completion summary with commit hashes and instruct `git push` (do NOT auto-push).
3. Run skill-crystallization detection for the next iteration.

## Inputs & Outputs

| Input | Source |
|-------|--------|
| Architecture/design doc with improvement list | `docs/<arch>.md` (e.g., `docs/3-repo-architecture.md`) |
| Current state of target files | Workspace files (`*.md`, `*.instructions.md`) |
| Cross-reference templates (e.g., index doc structure) | Same architecture doc, typically in §7 |

| Output | Format |
|--------|--------|
| Plan file | `.github/plans/<arch-prefix>-<repo>-improvements.md` |
| Updated instruction file(s) | Companion-tools blockquote inserted; `revision:` bumped |
| Updated agent file(s) | New `tools:` entries + new Stage; `revision:` bumped |
| New index doc | `docs/<topic>-ecosystem.md` with lookup table + pitfalls |
| Audit report (in commit message) | List of files scanned + classification (illustrative vs template-data) |
| Per-task git commits | `[Plan: <plan-name>] Task X.Y: ...` |

## Common Pitfalls

- **Fabricated cross-repo links.** When the target Repo B/C does not exist yet, use `(link TBD)` consistently. Grep for it during regression check (`grep -c '(link TBD)'`) — any missing placeholder means a fabricated URL slipped in.
- **Forgetting revision bump.** Each `*.md` and `*.instructions.md` modification must bump `revision:`. Easy to miss when the change is a tool addition or a single Stage insertion. Make it part of the same `multi_replace_string_in_file` call as the content edit, not a separate step.
- **Stage letter renumbering.** When inserting a new Stage between two existing ones, do NOT renumber subsequent Stages (E→F→G). Use a non-sequential letter like `Stage X` to indicate "extra/inserted gate" — preserves all internal references to original Stage E/F/G.
- **YAML breakage from indentation drift.** When inserting tool entries into the `tools:` list, copy the indentation pattern from existing entries exactly. Always verify with `python3 -c "import yaml; yaml.safe_load(open(f).read().split('---')[1])"`.
- **Audit task scope creep.** The audit task is read-only — it produces a classification report in the commit message, NOT file edits. If the audit reveals migration candidates, record them but defer migration to the destination repo's plan.
- **Missing fallback for unavailable MCP tools.** When declaring tools that don't exist yet (e.g., `openmc-validator/*` before Repo B exists), ensure the agent workflow has a documented fallback path or graceful degradation note. OpenCode silently ignores unavailable tools, but the agent workflow should not assume the tool was called successfully.
- **Plan and target file in separate commits.** Keep the `✅` plan marker and the target file edit in the SAME commit — protects resumability of the Task Executor mode.

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-04-26 | Initial crystallization | openmc-repo-a-improvements (5 tasks: openmc instruction companion tools + simulation-builder Stage X + simulation-analyst MCP postproc + audit + ecosystem index doc; commits d194c55..3606f81) |
