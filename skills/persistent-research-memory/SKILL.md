---
name: persistent-research-memory
description: "Persistent research memory across sessions — knowledge graph loading/updating, cross-session context retrieval, memory distillation triggering. Use when: starting a new research session that builds on prior work, ending a session with discoveries to persist, searching past research context. 持久化研究记忆：跨 session 知识图谱、上下文检索、记忆蒸馏触发。"
revision: 1
---

# Persistent Research Memory

## When to Use

- Starting a new research session that builds on prior simulation/analysis work
- Ending a session where you discovered new physical ranges, solved problems, or found parameter optima
- Searching for past results before re-running expensive simulations
- Ensuring continuity in multi-session research campaigns (TBR sweeps, activation chain analysis, etc.)
- Building a cumulative knowledge base of simulation results with provenance

## When NOT to Use

- For single-session, self-contained tasks (no need for persistence)
- For recording raw conversations (use session-memory MCP directly)
- For agent governance patterns — use `memory-distiller` DR1-DR6 rules

## Workflow

### At Session Start: Load Context

```
1. session-memory/memory_recall(task_description="<current session goal>")
   → Returns relevant past conversations with ±2 surrounding turns
2. Read memories/repo/knowledge-graph.md
   → Search for CS nodes matching current parameters
3. If CS node exists with status: converged → trust the reconciled value
4. If CS node exists with status: conflicting → flag for investigation
5. Read memories/repo/workflow-patterns.md for reusable patterns
```

### During Session: Record Key Decisions

When you encounter:
- A new physical range validated against simulation (→ DR2 candidate)
- A recurring error with a successful fix (→ DR1 candidate)
- A parameter configuration that produced good results (→ DR7 candidate)

Record these in your session context for end-of-session distillation.

### At Session End: Distill

Trigger `memory-distiller`:

```
You are the knowledge distiller. Distill this session's discoveries into
the knowledge graph at memories/repo/knowledge-graph.md.

Key events this session:
[list of: new ranges, errors+fixes, parameter configurations, key results]
```

Or trust the weekly scheduler to pick up the session automatically.

## Cross-Session Entity Format

When recording parameter sweep results or simulation outcomes that should persist:

```markdown
### CS-<id>: <descriptive title>

- **Sessions**: <session_date> (<agent>), <session_date> (<agent>)
- **Parameters**: <key=value pairs>
- **Consensus Value**: <quantity> ± <uncertainty> (<confidence level>)
- **Status**: converging | converged | conflicting
- **Related**: <links to other nodes>
- **Data**: <file path or commit hash>
- **Loading**: `session-memory/memory_recall(task_description="<context>")`
```

## Nuclear Engineering Applications

### Pattern: TBR Sweep Across Sessions

Session 1: TBR sweep breeder_thickness ∈ [3,6] cm → max TBR at 4.5 cm
Session 2: TBR sweep Li6_enrichment ∈ [30,90]% at fixed 4.5 cm → max at 60%
→ DR7 creates CS node reconciling both: TBR_max = 1.12 ± 0.03 at (4.5cm, 60%)

Session 3 starts: loads CS node → skips re-sweeping, proceeds to next variable.

### Pattern: Activation Product Library Building

Session 1: FISPACT run for EUROFER → 500 nuclides
Session 2: FISPACT run for SS316 → 480 nuclides
→ DR7 links overlapping activation products, builds cross-material activation library.

## Integration with Other Skills

- **experimental-design**: CS nodes hold DOE design matrices → load for augmentation
- **parametric-sweep**: CS nodes hold sweep results → skip redundant sweeps
- **pymatgen-materials**: CS nodes hold material screening results → cumulative knowledge

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-07-13 | Initial creation — inspired by cognee persistent memory architecture, adapted for nuclear engineering research continuity | Agent science capability upgrade plan |
