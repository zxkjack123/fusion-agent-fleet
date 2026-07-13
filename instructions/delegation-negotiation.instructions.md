---
description: "When and how agents should delegate tasks to other agents — decision trees for autonomous delegation. 委派协商：agent 何时自主决定委派给其他 agent 的决策树。"
applyTo: "**"
version: 1
revision: 1
---

# Delegation Negotiation Protocol — 委派协商协议

## When to Delegate — 何时委派

Agents should autonomously decide to delegate when any of these conditions are met. **User approval is NOT required** for these — agents should use judgment.

| Condition | Delegate to | Example |
|-----------|------------|---------|
| **Numerical output produced** (any quantity with units) | `background-reviewer` | TBR=1.15 → `@background-reviewer` |
| **Structural change made** (new agent/skill/instruction) | `doc-maintainer` | Created new agent → `@doc-maintainer` |
| **Uncertainty > 30%** (confidence < 70%) | `critical-thinking` | "I'm not sure if this assumption holds..." |
| **Final deliverable ready** | `doublecheck` | Pre-submission final check |
| **Multi-code chain produced results** (OpenMC→FISPACT→analysis) | `experiment-tracker` | Chain completed → snapshot all results |
| **Physical value outside expected range but not flagged** | `plausibility-check` | TBR=0.47 — is this real or a bug? |
| **Need domain knowledge** (nuclear data, materials, physics) | `dify-knowledge/global_search` or `nuclear-data-mcp` | "What's the (n,g) cross-section for Fe-56?" |

## When NOT to Delegate

| Condition | Do NOT delegate | Reason |
|-----------|----------------|--------|
| Pure file I/O | any agent | Direct `read`/`write` is faster |
| Simple calculation | any agent | Agent overhead > compute time |
| Already in a delegation chain (depth > 2) | any agent | Avoid infinite delegation loops |
| Self-delegation: same agent as caller | the calling agent itself | Do inline execution instead — avoid pm-coordinator → pm-coordinator or any agent → same agent recursion |
| User explicitly said "run this yourself" | any agent | Respect user intent |
| Subagent needs user input | call question() directly | Return NEEDS_USER_DECISION to parent agent — see AGENTS.md §5 for format |

## Decision Tree

```
Agent produces output
│
├─ Contains numerical values? ───→ @background-reviewer
│
├─ Modified agent/skill/instruction? ───→ @doc-maintainer
│
├─ Confidence < 70%? ───→ critical-thinking
│
├─ Is this a final deliverable? ───→ doublecheck
│
├─ Multi-code chain? ───→ experiment-tracker
│
└─ None of above ───→ handoff: USER
```

## Escalation Protocol

If an agent encounters an error it cannot fix:

```
Attempt 1: Self-diagnose and fix
Attempt 2: Self-diagnose again (different approach)
Attempt 3+: ↑ ESCALATE: <most_relevant_agent> — <error_summary>

Never silently skip an error. Escalation is better than silent failure.
```

## Recording Delegations

All delegations should be recorded in the agent's output for transparency:

```
Delegation Log:
  → background-reviewer: checked TBR=1.15, keff=0.38
  → doc-maintainer: updated _project-snapshot.md (new agent created)
  → critical-thinking: challenged Li-6 enrichment assumption
```

## See Also

- `AGENTS.md` §Agent Collaboration Protocol — handoff conventions and gate triggers
- `instructions/skill-crystallization.instructions.md` — when to crystallize workflows
- `scripts/pattern_tracker.py` — automated pattern tracking

## Deep-Chain Propagation

When an agent is in a delegation chain (parent → child → grandchild → ...):

1. At ANY depth, if a sub-agent returns `NEEDS_USER_DECISION`, its immediate parent must propagate it upward
2. The top-level agent (closest to the user) presents the question via `question()`
3. The user's answer flows back down the chain to the original sub-agent

### Deep-Chain Example

```
FDR → task-executor → academic-writer → format-engineer (depth 6)
  │                                              │
  │                                    format-engineer returns NEEDS_USER_DECISION
  │                                              │
  │                                    academic-writer detects it → propagates
  │                                              │
  │                                    task-executor detects it → propagates
  │                                              │
  └──────────────────────────────────── FDR detects it → question() to user
                                         │
                                    User answers → answer flows back down the chain
                                         │
                                    FDR → task-executor → academic-writer → format-engineer
```

### Parallel Sub-Agent Propagation

```
FDR
  ├→ Explore (running)
  ├→ Scientific Paper Research (NEEDS_USER_DECISION)
  └→ Dify KB Manager (running)

FDR detects NEEDS_USER_DECISION from SPR:
  1. Save Explore's output locally
  2. Save Dify KB Manager's output locally  
  3. Pause processing their results
  4. Present SPR's question to user
  5. User answers → re-delegate SPR with answer
  6. Resume processing saved Explore + Dify outputs
```
