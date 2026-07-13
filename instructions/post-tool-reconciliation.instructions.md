---
description: "Post-tool reconciliation trace requirement for DeepSeek V4 Pro agents. Forces explicit re-reasoning after each significant tool call to prevent silently ignoring contradicting results. Applies to all DeepSeek agents performing data analysis, simulation verification, or literature search. 工具调用后调和追踪：强制 DeepSeek 在每次工具调用后显式重新推理，防止静默忽略矛盾结果。"
applyTo: data-analyst,simulation-analyst,simulation-builder,doublecheck,fusion-chain-runner,scientific-paper-research,fusion-deep-research
target_agents:
  - data-analyst
  - simulation-analyst
  - simulation-builder
  - doublecheck
  - fusion-chain-runner
  - scientific-paper-research
  - fusion-deep-research
version: 1
revision: 1
---

# Post-Tool Reconciliation Trace — 工具调用后调和协议

DeepSeek V4 Pro's most dangerous failure mode is not producing wrong answers — it's producing correct tool calls and then **ignoring the tool result** when it contradicts the model's prior reasoning. The model's implicit chain-of-thought anchors on its initial belief, and contradictory evidence from tools is silently skipped.

This protocol forces explicit re-reasoning after every significant tool call, implementing the CRITIC pattern (Gou et al., arXiv:2305.11738, ICLR 2024) end-to-end.

## When to Apply

Mandatory for all DeepSeek V4 Pro agents when:
- A tool call returns a quantitative result (number, measurement, table)
- A verification tool returns a PASS/FAIL/WARNING verdict
- A search tool returns zero results or results that don't match the query expectation
- A plausibility check produces a result outside the expected range

Skip for:
- Metadata operations (listing available knowledge bases, checking MCP health)
- File I/O with no data content (file existence, directory listing)
- Purely procedural calls with no substantive return value

## Protocol

After each qualifying tool call, produce a **3-line reconciliation trace** before making the next decision:

```
[Tool] <tool_name> returned: <key result, ≤1 line>
[Prior] My reasoning was: <belief before this call, ≤1 line>
[Conclusion] This [CONFIRMS | CONTRADICTS | REFINES | IS UNRELATED TO] my prior because <why>. Updated direction: <what changes>
```

### Key Rules

1. **CONTRADICTS has the highest weight**. If the tool result actively contradicts prior reasoning, the model MUST update its belief. Do not rationalize the contradiction away.
2. **CONFIRMS must be explicit about what's confirmed**, not generic. "CONFIRMS my prior because the TBR falls within my expected range of 0.95-1.25" — not just "CONFIRMS."
3. **Zero results are not empty**. "Found 0 papers about X" IS a signal — document it. Does it mean the search terms are wrong? The query is too narrow? The area is genuinely unexplored?
4. **IS UNRELATED TO is valid but must be justified**. If a tool result genuinely doesn't affect the reasoning, state why — "This format validation result is orthogonal to whether the physics setup is correct."

### Batch Reconciliation

When multiple tool calls are made in parallel (e.g., Dify KB + S2 + web crawl), produce a **batch reconciliation** after all results arrive:

```
[Batch Reconciliation]
- [Tool A] returned X → [CONFIRMS prior about Y]
- [Tool B] returned Z → [CONTRADICTS prior about W, updating...]
- [Tool C] returned empty → [REFINES prior: search scope too narrow, broadening...]
Synthesis: <1-2 line updated understanding>
```

## Severity Escalation

When a CONTRADICTS is detected:

| Old Confidence | Tool Result Type | Action |
|---------------|-----------------|--------|
| HIGH | Tool says opposite | **STOP** — do not proceed. Re-examine the basis of the original belief. The model was confidently wrong. |
| HIGH | Tool says "range is wider/narrower" | Reduce confidence to MEDIUM. Document the refinement. |
| MEDIUM | Tool says opposite | Abandon prior. Adopt tool-verified position. |
| LOW | Tool says anything | Trust the tool fully. |
| Any | Tool is plausibility-check returning FAIL | **HARD STOP** — physical impossibility detected. Escalate to CT or user. |

## Anti-Patterns (what DeepSeek tends to do)

**❌ Rationalizing contradiction as nuance**:
> "The tool says peak < average, but that's probably because of the mesh zoning effects..."
→ WRONG. peak < average is physically impossible. The tool result is not "nuanced" — it's a signal of a bug.

**❌ Treating zero results as confirmation**:
> "No papers found on this exact combination — this confirms the idea is novel."
→ WRONG. "No results" could mean: wrong search terms, too narrow query, insufficient literature. It does NOT confirm novelty without further investigation.

**❌ Ignoring the second CONTRADICTS when the first was resolved**:
> Tool A contradicted → fixed → Tool B contradicts → assumes it's the same issue.
→ WRONG. Each tool contradiction must be independently reconciled.

**❌ Updating the conclusion without updating the confidence**:
> "Prior was CONTRADICTED, now adopting new value. Conclusion: result is X±Y."
→ WRONG. If the prior was contradicted, the new conclusion starts at LOW confidence until independently verified.

## Integration with Existing Harness

This protocol is complementary to:
- **CoT Externalization Rules**: CoT runs BEFORE tool calls; reconciliation runs AFTER. Together they enforce full pre→tool→post reasoning.
- **CT Red Flag Issue Ledger**: CONTRADICTS findings that cannot be resolved are exactly the kind of issues that should appear in the ledger.
- **Pre-Delivery Audit**: Reconciliation traces serve as evidence for §3 (Order-of-Magnitude Sanity) and §4 (Conservation & Consistency Law) checks.
