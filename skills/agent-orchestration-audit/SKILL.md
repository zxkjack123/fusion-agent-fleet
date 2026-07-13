---
name: "agent-orchestration-audit"
description: "Audit and remediate orchestrator-style *.md files for the agent-capability-awareness-gap pattern: zombie subagent declarations, missing pre-flight availability checks, narrow capability descriptions in workflow body, and missing escalation chains before declaring 'X unavailable'. Use when an orchestrator agent reports 'private KB not loaded / full text needs another team' WITHOUT trying its declared subagents, or when frontmatter `agents:` list contains entries never invoked in the workflow body. Agent capability awareness gap, zombie subagent detection, escalation chain template, pre-flight matrix, 子代理能力盲区, 僵尸代理清理, 升级链补全, 预检矩阵, orchestrator audit."
revision: 1
---

# Agent Orchestration Audit

> Crystallized from: fusion-deep-research + presentation-architect + patent-writer + proposal-writer remediation campaign — fixed agent-capability-awareness-gap pattern across 4 orchestrators
> Date: 2026-04-26
> Trigger: T3 (user explicit confirmation after near-certain pattern recurrence; confidence 0.9)

## When to Use

- An orchestrator-style `*.md` reports "X unavailable / cannot retrieve / 需要其他子系统" WITHOUT first attempting its declared subagents.
- Frontmatter `agents:` contains entries that grep-search of the body never references (zombie declarations).
- A workflow stage talks about delegation only at the terminal export step, leaving mid-stage retrieval/analysis blind to subagent capabilities.
- A "MCP unavailable fallback" branch silently skips the dependent step instead of routing to a subagent that could substitute.
- User reports an agent surfaced a capability gap that another already-declared subagent could have closed.

## When NOT to Use

- Single-tool-budget trim with no subagent question → use `agent-tool-budget-trim` skill.
- Boundary/role overlap between sibling agents → use `agent-fleet-boundary-cleanup` skill.
- Drafting a brand-new orchestrator from scratch → use `agent-customization` skill.
- Pure prose polish of existing agent description → direct edit, no skill needed.

## Workflow

### Phase 0 — Pattern detection per agent

For each candidate `*.md`, collect four signals:

1. **Zombie declarations.** Parse frontmatter `agents:` array. For each name, grep the body for the exact name string. Names with zero body matches are zombies.
2. **Missing pre-flight matrix.** Search the body for `Pre-flight` or `Availability Check` near the workflow header. If absent, the agent has no proactive capability probing.
3. **Narrow capability description.** For each declared subagent, check whether the body mentions it at exactly one stage with a single keyword (e.g. only "Diagram Architect for export"). Single-keyword bindings prevent mid-stage fire.
4. **Missing escalation chain.** Search for phrases like "unavailable → skip", "fallback: skip", "if X not loaded, omit". These should be replaced by a multi-step escalation chain BEFORE any user-facing "unavailable" tag.

Output an audit table per agent with one row per signal and a SEVERE/WARN/OK severity. Do NOT modify files yet.

### Phase 1 — Remediation plan

For each agent flagged SEVERE, plan four edits:

A. **Clean zombies.** Remove zombie names from `agents:`. If a body mention exists for a name NOT in `agents:` (the inverse zombie), add the missing name.
B. **Inject pre-flight matrix.** Insert directly after the `## Workflow` header, before Stage A:
   - A capability-table listing each declared subagent with its full capability scope (not just the one workflow trigger).
   - A `Pre-flight: Subagent / Tool Availability Check` block that probes each subagent + each MCP family used in the workflow, recording `<NAME>_OK` flags.
   - A `for each false flag` block listing the explicit fallback path (route to substitute subagent / queue manual import / tag self-audit). Forbid silent skips.
C. **Inject escalation chain.** For each user-facing "unavailable" surface (literature, full text, evidence, raw data, processed figures), prepend a mandatory N-step escalation list (typical N=3–5) ending with: "Only after exhausting all may you tag `[⚠️ ...]` and record attempt trace `[尝试: A✗ B✗ C✓abstract-only]`".
D. **Bump revision.** Increment `revision:` integer in frontmatter.

### Phase 2 — Apply edits and validate

1. Apply edits with multi-replace per file. Keep edits surgical: do NOT restructure existing stages.
2. Re-grep the body for each name in `agents:` — every name must have ≥1 body match.
3. Re-grep for "unavailable" / "skip" — every match must be under an escalation chain or have a documented justification.
4. Run `python3 scripts/check_agent_tool_budget.py` if the project provides one — confirm no FAIL regression.
5. Commit per-agent (one revision bump per commit).

### Phase 3 — Repo memory update

1. Append the audit + remediation to `/memories/repo/workflow-patterns.md` under `## agent-capability-awareness-gap`, with `last_seen` and an evidence entry.
2. Increment count and recompute confidence per `instructions/skill-crystallization.instructions.md` rules.

## Inputs & Outputs

| Input | Source |
|-------|--------|
| Orchestrator `*.md` files | Repo root or fleet directory |
| Optional budget script | `scripts/check_agent_tool_budget.py` |
| Repo memory | `/memories/repo/workflow-patterns.md` |

| Output | Format |
|--------|--------|
| Per-agent audit table | Markdown rows: signal × severity × evidence |
| Edited `*.md` files | Revision bumped, frontmatter cleaned, pre-flight + escalation injected |
| Updated workflow-patterns.md | Append-only entry with date + agent name |

## Reference Templates

### Pre-flight matrix template (drop directly under `## Workflow` header)

```markdown
### Subagent Capability Reminder & Escalation Policy

This agent delegates <retrieval / novelty / logic / analysis / diagram refinement> to the following subagents. Treat them as first-class capabilities, not last-resort fallbacks.

| Subagent | Full capability scope | Trigger in this workflow |
|----------|----------------------|--------------------------|
| `<Subagent A>` | <full tool list / domain> | <stage trigger> |
| `<Subagent B>` | ... | ... |

**Pre-flight: Subagent / Tool Availability Check** (run once at Stage A start).

1. Probe each subagent above; record `<NAME>_OK` flag.
2. Probe each MCP family with one trivial call; record `<MCP>_OK`.
3. For each `false` flag, plan a fallback path NOW — do NOT silently skip dependent steps:
   - `<NAME>_OK = false` → <explicit substitute or self-audit path>
   - ...
```

### Escalation chain template (drop near each "unavailable" surface)

```markdown
**<Resource> gap escalation (mandatory).** Before declaring "<unavailability>" to the user, you MUST attempt in this order:

1. <subagent broadest>
2. <MCP curated KB>
3. <web crawl + landing page>
4. <local indexed library>
5. <preprint / repo fallback>

Only after exhausting all may you tag `[⚠️ <unavailability>]` and record attempt trace, e.g. `[尝试: A✗ B✗ C✓abstract-only]`.
```

### Zombie detection one-liner (Python)

```python
import re, sys, yaml
from pathlib import Path

for f in Path('.').glob('*.md'):
    text = f.read_text()
    m = re.match(r'---\n(.*?)\n---', text, re.S)
    if not m: continue
    fm = yaml.safe_load(m.group(1))
    body = text[m.end():]
    declared = fm.get('agents', []) or []
    zombies = [a for a in declared if a not in body]
    body_mentions = re.findall(r'`([A-Z][A-Za-z ]+?)`', body)  # crude
    if zombies:
        print(f'{f.name}: zombies = {zombies}')
```

## Common Pitfalls

- **Treating a subagent as single-purpose** because its first body mention is narrow. Always re-list the full capability scope in the pre-flight table — one keyword in a stage description is not enough to trigger mid-stage fire.
- **Removing a zombie that the body actually uses under a different casing or backtick form.** Always grep both with and without backticks, and case-insensitively, before deleting from `agents:`.
- **Adding a subagent to `agents:` whose tools the parent agent already holds directly.** This duplicates capability and inflates budget. If the body call is to a tool the parent owns, do not add the subagent — adjust the body to call the tool directly.
- **Pre-flight that probes too aggressively.** A no-op probe per subagent on every invocation is wasteful. Probe once at Stage A start and cache `*_OK` flags for the rest of the run.
- **Escalation chain that stops at "abstract only".** Always include at least one local-library or preprint fallback so users get more than metadata before seeing the warning tag.
- **Silent skip survives the edit.** After injecting the escalation chain, re-grep for the original "skip" / "unavailable" phrases — they must now sit UNDER the chain, not parallel to it.
- **Bumping revision but forgetting to update workflow-patterns.md.** This breaks the T2 trigger detection for future audits.

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-04-26 | Initial crystallization | fusion-deep-research + presentation-architect + patent-writer + proposal-writer remediation (4 orchestrators, agent-capability-awareness-gap pattern) |
