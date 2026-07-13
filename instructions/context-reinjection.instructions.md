---
description: "Compaction 后自动重新注入关键 guardrail 规则的约定。Context rot prevention protocol. 上下文腐烂防护：compaction 后自动恢复关键规则。"
version: 1
revision: 1
applyTo: "**"
---

# Context Re-Injection — 上下文重新注入

Agent 在长对话中遇到 compaction 时，opencode 会裁剪早期的上下文以保持在 token 预算内。关键 guardrail 规则（如在 session 开始时注入的 `AGENTS.md Domain Experience Bootstrap`、`numerical-intuition-pitfalls` 等）可能在 compaction 后丢失。

本协议定义了 agent 在检测到 compaction 后应执行的恢复操作。

## When to Re-Inject

以下任一条件满足时执行：
1. Agent 在对话中发现 compaction 标记（如 opencode 的 `[compacted]` 或消息被截断）
2. Agent 无法在上下文中找到初始注入的 `## Domain Experience Bootstrap` 或其他关键规则
3. 对话超过 10 轮 — 默认假设至少有一次 compaction 可能已发生

## What to Re-Inject

按优先级注入以下最小摘要：

1. **Numerical Intuition Pitfalls §1**（物理不可能值）:
   - peak < average → 物理不可能，立即停止
   - 负截面/负通量/负浓度 → 物理不可能
   - keff < 0.5 or > 1.5 → 检查模型是否正确

2. **Post-Tool Reconciliation**（3-line trace 格式）:
   - 每次数据产生工具调用后，输出 `[Tool] | [Prior] | [Conclusion]`

3. **Handoff Convention**:
   - 数值输出 → `@background-reviewer`
   - 结构性变更 → `@doc-maintainer`
   - 高不确定性 → `critical-thinking`

4. **Vision Tools**:
   - `vision_query(image, prompt)` — describe/read a single image
   - `vision_compare(image, prompt, providers)` — parallel multi-model cross-check
   - For deep multi-figure analysis, delegate to `figure-analyst`

## How to Re-Inject

Agent 在检测到需要恢复时，在对话中写一条简短的声明：

```
[Guardrails Restored — compaction detected, critical rules re-injected:
  § Numerical intuition: peak<avg → impossible; negative values → impossible
  § Reconciliation: [Tool]|[Prior]|[Conclusion] after each data call
  § Handoffs: @background-reviewer for numerical, @doc-maintainer for structural
  § Vision: vision_query() / vision_compare() for image analysis; figure-analyst for multi-figure review]
```

不完整复制原规则全文 — 精要摘要即可（≤80 tokens）。

## Fallback

如果对话尚未发生 compaction，不需要显示恢复声明。

## See Also

- `AGENTS.md` §Domain Experience Bootstrap — session 开始时注入的参考
- `instructions/post-tool-reconciliation.instructions.md` — 调和追踪
- `instructions/numerical-intuition-pitfalls.instructions.md` — §1 硬停止规则
