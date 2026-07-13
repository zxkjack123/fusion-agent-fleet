---
description: "Factcheck quality gate: mandatory fact verification before delivering any document containing factual claims. 事实核查交付门禁, 声明验证, 数值校验, 引用核查, 方法论验证."
applyTo: "academic-writer,patent-writer,proposal-writer,review-responder"
revision: 1
---

# Factcheck Gate — 事实核查交付门禁

**触发条件**: 任何适用 agent 在交付包含事实性声明的产出前，**必须**执行本检查。检查未通过则**阻断交付**，修复标记问题后重新检查。

**适用范围**: 所有产出包含可验证事实声明（数值、引用、方法论能力、物理事实）的工作流。Phase 3 scope = 4 highest-risk producers; expansion in R2.

**执行位置**: 置于 De-AI-Fier Gate **之后**、Pre-Delivery Audit **之前** — 先修正文本表达，再核查事实，最后做物理合理性审核。

## Level Classification — 分级策略

根据产出文本中事实声明的密度和风险选择检查深度：

| Level | 适用场景 | 检查方法 |
|-------|----------|----------|
| **L0-Skip** | 纯格式/翻译/排版操作，无事实声明 | 不适用 |
| **L1-Lite** | ≤10 factual claims，或仅涉及低风险定性描述 | Self-check: agent 自行对每条 claim 标注来源，无来源的标记 `[⚠️ unverified]` |
| **L2-Standard** | >10 factual claims OR 含数值数据/引用 | Delegate to `Doublecheck` (max_cycles=1) |
| **L3-Critical** | Safety-related claims (dose, TBR, criticality), 含剂量/活化/临界参数 | Delegate to `Doublecheck` (max_cycles=2) + require programmatic anchors for all NUMERICAL claims |

## L0-Skip Procedure

1. Verify output contains no factual claims (only formatting, translation, or structural changes).
2. Append confirmation: `[Factcheck Gate: L0-Skip — no factual claims]`

## L1-Lite Procedure

1. Extract all factual claims from the output (≤10 expected).
2. For each claim, verify provenance: is a source cited or is the claim common knowledge?
3. Mark any unsourced non-trivial claim with `[⚠️ unverified]`.
4. If all claims have sources or are common knowledge → PASS.
5. If any claim is marked `[⚠️ unverified]` → attempt source recovery (quick search). If found, add source. If not found, flag for user attention.
6. Append confirmation: `[Factcheck Gate: L1-Lite PASS]` or `[Factcheck Gate: L1-Lite PASS with N warnings]`

## L2-Standard Procedure

1. Delegate to `Doublecheck` with the output text and `max_cycles=1`.
2. Receive Doublecheck's verification report.
3. Evaluate results:
   - If 0 🔴 items and ≤2 🟡 items → PASS (append 🟡 items as advisory notes).
   - If any 🔴 item → FAIL. Fix flagged claims and re-run.
   - If >2 🟡 items → CONDITIONAL PASS. User must acknowledge 🟡 items before delivery.
4. Append confirmation: `[Factcheck Gate: L2-Standard PASS]`

## L3-Critical Procedure

1. Delegate to `Doublecheck` with the output text and `max_cycles=2`.
2. Require that Doublecheck's Layer 2.5 Programmatic Anchors are applied to all NUMERICAL claims.
3. Evaluate results:
   - If 0 🔴 items and 0 🟡 items → PASS.
   - If any 🔴 OR any 🟡 on safety-related claims (dose, TBR, criticality, activation) → FAIL. No conditional pass for safety claims.
   - Other 🟡 items on non-safety claims → CONDITIONAL PASS with mandatory user acknowledgment.
4. Append confirmation: `[Factcheck Gate: L3-Critical PASS]`

## MCP Unavailable Fallback — Doublecheck 不可用降级

If `Doublecheck` agent is unavailable (timeout, sub-agent failure, MCP infrastructure down):

1. **Do NOT block delivery indefinitely.** Downgrade to L1-Lite self-check.
2. Perform L1-Lite procedure (self-check of all claims).
3. Append: `[Factcheck Gate: DEGRADED — Doublecheck unavailable, L1-Lite self-check applied]`
4. Warn the user: `⚠️ Factcheck gate was degraded because Doublecheck is unavailable. Manual review of factual claims is recommended before external delivery.`
5. Proceed to Pre-Delivery Audit.

## Integration Pattern — Agent 集成模板

在 agent 的 Quality Gate / Delivery 阶段添加一行引用即可：

```
N. **Factcheck Gate**: Execute `instructions/factcheck-gate.instructions.md` at L2-Standard (downgrade to L1-Lite if output is pure-text polish with no new factual claims). **FAIL → block delivery.**
```

其中 `N` 为步骤编号，`L2-Standard` 可替换为 `L1-Lite` 或 `L3-Critical`（适用于安全相关场景）。

## Confirmation Markers — 确认标记

| 结果 | 标记 |
|------|------|
| L0-Skip | `[Factcheck Gate: L0-Skip — no factual claims]` |
| L1-Lite 通过 | `[Factcheck Gate: L1-Lite PASS]` |
| L2-Standard 通过 | `[Factcheck Gate: L2-Standard PASS]` |
| L3-Critical 通过 | `[Factcheck Gate: L3-Critical PASS]` |
| Doublecheck 不可用 | `[Factcheck Gate: DEGRADED — Doublecheck unavailable, L1-Lite self-check applied]` |
