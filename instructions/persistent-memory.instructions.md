# Persistent Memory Instructions

## Overview

This instruction set defines how agents should interact with the persistent research memory system, built on top of `memory-distiller`, `session-memory` MCP, and the knowledge graph at `memories/repo/knowledge-graph.md`.

## Knowledge Graph Node Types

| Node Prefix | Type | Created By | Purpose |
|-------------|------|-----------|---------|
| `N` | General Knowledge Node | DR1-DR6 rules | Recurring errors, physical ranges, solution patterns, agent bottlenecks, guardrail triggers, harness bottlenecks |
| `CS` | Cross-Session Entity Node | DR7 rule | Parameter configurations, material combinations, code versions that appear across ≥2 sessions |
| `E` | Edge | Linking | confirms, contradicts, supersedes, complements, depends_on |

## Retrieval Patterns

### Pattern 1: Before Starting Expensive Computation

```
1. session-memory/memory_recall(task_description="<describe the computation>")
2. Read memories/repo/knowledge-graph.md for CS nodes with matching parameters
3. If CS node exists and status=converged: use the stored result, skip re-computation
4. If CS node exists and status=conflicting: determine if new run resolves the conflict
```

### Pattern 2: After Discovery of a New Physical Range

```
1. Check corpora/plausibility-ranges.yaml for existing range
2. If new value falls outside existing range AND is validated:
   - Record in session context for memory-distiller to pick up as DR2
   - Suggest range update to plausibility-ranges.yaml
```

### Pattern 3: Debugging a Recurring Error

```
1. session-memory/memory_search(query="<error keywords>")
2. Read knowledge-graph.md for N nodes matching the error pattern
3. If N node exists with "solution" type: follow the documented fix
4. If no N node exists: document the error+fix for memory-distiller DR1
```

## Context Window Re-Injection

When compaction drops early context, agents should self-re-inject:

1. Re-read `memories/repo/knowledge-graph.md` (CS nodes section)
2. Re-run `session-memory/memory_recall` for the current task
3. Re-read relevant `memories/repo/workflow-patterns.md` patterns

This is triggered automatically by `instructions/context-reinjection.instructions.md`.

## Durable Execution Link

Persistent memory works alongside `instructions/durable-execution.instructions.md`:
- `traces/checkpoint.json` tracks task completion
- `memories/repo/knowledge-graph.md` tracks research knowledge
- Together they enable session recovery + knowledge continuity

## When to NOT Distill

Do NOT distill:
- Transient debugging logs (only the final fix pattern)
- Single-use one-off queries
- Raw user-agent conversations (that's `session-memory`'s job)
- Knowledge already present in the graph (check before adding)

## Maintenance

- Run `python3 scripts/check_doc_freshness.py` weekly to verify knowledge graph freshness
- Stale CS nodes (>90 days without new confirming sessions) → mark `status: stale`
- Contradicted CS nodes → mark `status: superseded` with edge to the new node

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-07-13 | Initial creation — persistent memory retrieval/distillation patterns for all agents | Agent science capability upgrade plan |
