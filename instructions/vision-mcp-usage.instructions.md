---
description: "Vision MCP tool usage policy: when and how to use vision_query and vision_compare for image analysis, and when to delegate to figure-analyst instead"
applyTo: "**"
revision: 1
---

# Vision MCP Tool Usage Policy

The `vision` MCP server (registered globally in `~/.config/opencode/opencode.jsonc`) provides two tools for image analysis. All agents inherit this policy.

## Available Tools

### `vision_query` — Single-Model Vision

```
vision_query(image_path: str, prompt: str, provider: str = "auto") -> TextResult
```

- **Use for**: Chart reading, OCR, photo description, single-image analysis
- **Provider chain** (when `auto`): GPT-5.5 → Claude Opus → Kimi-K2.6 → Qwen3.6-Plus → Ollama (local)
- **Cost**: ~$0.01-0.05/call (GPT-5.5 hit); ~$0.001 (fallback to SCNet providers)
- **Timeout**: 30s per provider attempt

### `vision_compare` — Parallel Multi-Model Cross-Validation

```
vision_compare(image_path: str, prompt: str, providers: list[str] = ["gpt-5.5", "claude-opus", "kimi"], require_consensus: bool = False) -> CompareResult
```

- **Use for**: Critical numerical data extraction, figure-text discrepancy checks, verification
- **Execution**: All specified providers queried in parallel; results merged and cross-compared
- **Output**: `{consensus, confidence (HIGH/MEDIUM/LOW), individual_results, discrepancies}`
- **Cost**: ~$0.03-0.10/call (3 providers parallel)

## Decision Tree

```
Agent encounters an image
          │
          ▼
  ┌─────────────────────────────────┐
  │ Is this a critical numerical     │
  │ value? (TBR, k_eff, DPA, dose,   │
  │ material composition, isotope %) │
  └────────────┬────────────────────┘
       Yes     │     No
       ┌───────┘     └──────────────┐
       ▼                             ▼
vision_compare()              ┌────────────────────┐
(2-3 providers,               │ Is this a full       │
 require_consensus=true)       │ figure review with   │
                               │ multiple images or   │
                               │ deep visual analysis?│
                               └────────┬───────────┘
                                  Yes   │   No
                                  ┌─────┘   └──────┐
                                  ▼                ▼
                          task(figure-analyst)  vision_query()
                          (dedicated vision    (auto provider)
                           model agent)
```

## Failure Handling

| Scenario | Behavior |
|----------|----------|
| All providers fail | `vision_query` returns `ToolError` with error details; agent should report to user |
| `vision_compare` partial (2/3 providers respond) | Returns result with `confidence: "MEDIUM"`; agent decides whether to accept |
| `vision_compare` majority (1/3) | Returns result with `confidence: "LOW"`; agent MUST NOT cite as verified data |
| Image file not found | Immediate `ToolError` — verify path before calling |
| Image > 20MB | Immediate `ToolError` — resize before calling |

## When NOT to Use Vision Tools

- **Multi-figure comparative analysis** with iterative visual reasoning → delegate to `figure-analyst`
- **Figure quality review** (pixel-level: text overlap, color contrast, label readability) → delegate to `figure-quality-reviewer`
- **Tasks where image is not the primary focus** and text-based tools suffice → don't use vision tools

## Context Preservation

Unlike `task(subagent)`, MCP tool calls preserve the calling agent's full context. DeepSeek V4 Pro agents can:
1. Call `vision_query` to read a chart
2. Receive text result inline in the same conversation
3. Continue reasoning with the extracted data — no context switch

## See Also

- `AGENTS.md` §Vision Tool Availability
- vision-mcp-server: [docs/architecture.md](https://github.com/zxkjack123/vision-mcp-server/blob/main/docs/architecture.md)
- vision-mcp-server: [docs/agent-collaboration.md](https://github.com/zxkjack123/vision-mcp-server/blob/main/docs/agent-collaboration.md)
