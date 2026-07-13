---
description: "Cross-validation quality gate: mandatory complementary-axis check, sub-agent fallback, and merge-dedup for all agents using Pattern A or Pattern B. 交叉验证质量门禁, 互补轴检查, 子Agent容错, 合并去重."
applyTo: "paper-reviewer,innovation-reviewer,fusion-deep-research,academic-writer,proposal-writer,review-responder,teaching-assistant,diagram-architect,patent-writer"
revision: 1
---

# Cross-Validation Quality Gate — 交叉验证质量门禁

**触发条件**: 任何启用了 Pattern A（并行子 Agent 互补）或 Pattern B（顺序深度升级）的 agent 在交付前，**必须**通过本门禁检查。检查未通过则**阻断交付**，修复标记问题后重新检查。

**适用范围**: 仅启用了 Pattern A 或 Pattern B 的 agents。未启用多深度交叉验证的 agent 无需执行本检查。

**参考文档**: `docs/cross-validation-patterns.md` — 完整模式定义、决策树、兼容性矩阵。

---

## Pattern A Gate（并行子 Agent 互补）

### A1 — 互补轴清晰度检查

在发起 Pattern A 双路径之前，必须确认互补轴定义清晰：

| # | Check | Criterion |
|---|-------|-----------|
| 1 | 广度轴定义 | 明确了广度轴覆盖范围（≥80% of search space） |
| 2 | 深度轴定义 | 明确了深度轴覆盖范围（5-20% of search space） |
| 3 | 重叠区定义 | 两个轴存在 20-50% 的重叠——深度轴目标集 ⊆ 广度轴目标集 |
| 4 | 独立发现 | 每个轴都能发现对方不能发现的问题 |
| 5 | 方法差异 | 广度轴和深度轴使用**本质上不同**的分析方法（非同一方法的不同参数） |

**判定规则**:
- 5/5 PASS → 继续执行 Pattern A
- 1-4 项中有 FAIL → 停止，修正互补轴定义后再检查
- 第 5 项 FAIL → 考虑降级为 Pattern B（顺序深度升级），因为 axis 差异不够正交

### A2 — 子 Agent Fallback 规范

所有 Pattern A 的 coordinator agent **必须**实现以下三种 fallback：

#### Fallback 1: 子 Agent 超时

```
1. 子 agent 调用超过超时阈值（建议：5 分钟）→ 标记为 timeout
2. 超时子 agent 的结果置为 None
3. 继续等待未超时的子 agent
4. 合并阶段：仅用可用子 agent 的结果
5. 输出报告标注："⚠️ Partial — [Missing-Agent] 不可用（超时），仅单侧验证"
```

#### Fallback 2: 子 Agent 返回畸形输出

```
1. 子 agent 返回结果无法解析（非结构化、格式错误、空输出）
2. 重试 1 次（同样的 prompt，不同 request）
3. 若重试成功 → 使用重试结果
4. 若重试失败 → 标记该子 agent 为 unavailable
5. 合并阶段：仅用可用子 agent 的结果
6. 输出报告标注："⚠️ [Agent] 结果省略 — 格式错误（已重试 1 次）"
```

#### Fallback 3: 双路径结论冲突

```
1. 合并时发现：同一发现被两个子 agent 报告，但结论相反
2. 判定规则：深度轴（语义/方法论）的结论覆盖广度轴（模式/格式）的结论
3. 报告标注："🟡 冲突已解决 — [深度 Agent] 结论优先于 [广度 Agent]，针对 [发现]"
4. 冲突记录到输出报告的 Conflict Log 节
```

### A3 — 合并去重规范

```
输入:
  report_A: 广度轴子 agent 的报告（发现列表 F_A）
  report_B: 深度轴子 agent 的报告（发现列表 F_B）

算法:
  merged   ← []
  matched  ← {}  # B 中已被匹配的发现
  for f_a in F_A:
      best_match ← None
      best_score ← 0
      for f_b in F_B where f_b ∉ matched:
          score ← semantic_overlap(f_a, f_b)  # 基于相同的 target（文件名/claims）+ 相同的问题类别
          if score ≥ 0.8:
              best_match ← f_b
              best_score ← score
              break
      if best_match:
          matched.add(best_match)
          merged.append(merge_findings(f_a, best_match, confidence="high"))
      else:
          merged.append(f_a.with_tag("广度轴独有"))

  for f_b in F_B where f_b ∉ matched:
      merged.append(f_b.with_tag("深度轴独有"))

  按 confidence 排序: high → 广度独有 → 深度独有
  输出 merged

semantic_overlap(f_a, f_b):
  # 同名文件 + 同类别问题 → 视为 ≥80% 重叠
  if f_a.file == f_b.file and f_a.category == f_b.category:
      return 0.9
  # 仅同名文件 → 中等重叠
  if f_a.file == f_b.file:
      return 0.5
  # 同类别但不一定同文件 → 检查描述相似度
  return text_similarity(f_a.description, f_b.description)

merge_findings(f_a, f_b):
  # 保留更详细的版本（通常是深度轴的）
  detailed ← max(f_a, f_b, key=lambda f: len(f.description))
  detailed.confidence ← "high"  # 双路径确认
  detailed.cross_validated ← True
  return detailed
```

**输出格式要求**: 合并报告按三级分组呈现：
1. 🔴 **Dual-confirmed**（双路径确认）— 最高优先级
2. 🟡 **广度轴独有** — 中优先级
3. 🔵 **深度轴独有** — 中优先级

---

## Pattern B Gate（顺序深度升级）

### B1 — 深度级别定义检查

在输出前，确认三级深度已正确定义：

| # | Check | Criterion |
|---|-------|-----------|
| 1 | Quick 级别 | 检查项明确（如：语法、格式、术语） |
| 2 | Medium 级别 | 检查项明确（如：结构、流程、图表引用） |
| 3 | Thorough 级别 | 检查项明确（如：论证逻辑、证据、一致性） |
| 4 | Blocking 阈值 | Quick: 任何问题阻断；Medium: ≥3 问题阻断；Thorough: 任何问题阻断 |
| 5 | 深度升级顺序 | Quick → Medium → Thorough，不可跳级 |

### B2 — 顺序升级执行规范

```
1. 执行 Quick pass
   - 若发现 blocking issue → 修复所有 Quick 问题 → 重新执行 Quick
   - 若 0 blocking → 进入 Medium

2. 执行 Medium pass
   - 若发现 ≥3 blocking issues → 修复所有 Medium 问题 → 回到 Quick（完整重启）
   - 若发现 1-2 blocking issues → 修复 → 重新执行 Medium（本级重试）
   - 若 0 blocking → 进入 Thorough

3. 执行 Thorough pass（如适用）
   - 若发现 blocking issue → 修复所有 Thorough 问题 → 回到 Quick（完整重启）
   - 若 0 blocking → 通过门禁

最多 3 轮完整重启（Quick→修复→Quick 计 1 轮）。超过 3 轮仍 FAIL → 降级：
  降级策略：
  - 保留最近一次通过 Quick+Medium 的版本
  - 报告标注："⚠️ Thorough 级别审查未通过（已尝试 3 轮），交付 Medium-pass 版本"
```

### B3 — Issue Ledger 规范

每轮 Pattern B 重启必须维护一个 **Issue Ledger**，防止非单调漂移（详见 `docs/cross-validation-patterns.md` §Issue Ledger Protocol）。

**执行要求**：

1. 每轮 Quick/Medium/Thorough pass 结束时，emit 一个 ledger snapshot（issue_id + level + category + status）。
2. Restart 时携带上轮 ledger 作为上下文输入。
3. 新一轮 pass 的发现必须与 ledger 做 fingerprint 匹配：
   - 已存在 issue（fingerprint 命中） → 更新 `cycle_last_seen`，保持 OPEN
   - 旧 issue 未再出现 → 标记 CLOSED
   - 全新 issue（fingerprint 无匹配） → 追加到 ledger
4. **Monotone check**：若本轮 OPEN issue count > 上轮 OPEN count → gate FAIL。
   - 行为：停止继续重启，交付上轮版本（last-known-good），标注 `⚠️ Non-monotone drift — delivering prior-cycle version`。
5. Ledger 丢失（上下文截断等）→ 降级为全量重检（等同无 ledger 行为），标注 `⚠️ Ledger lost — full re-check`。

**门禁通过条件**（追加）：B1 + B2 + B3 + B4 全部满足。

### B4 — Tool-Feedback Breakpoints

在 Medium 和 Thorough pass 中，涉及**可验证声明**（数值、DOI、逻辑命题）的发现，必须经过工具调用确认后才能标记为 PASS/RESOLVED（详见 `docs/cross-validation-patterns.md` §Tool-Feedback Breakpoints (CRITIC Pattern)）。

**执行要求**：

1. 识别当前 pass 中所有涉及可验证声明的发现。
2. 对每个可验证声明调用对应工具（数值→plausibility-ranges, DOI→Crossref, 逻辑→pre-delivery-audit §1/§4）。
3. 工具确认 pass → 允许标记 PASS/RESOLVED。工具检测到矛盾/不匹配 → 升级该发现严重度一级。
4. **降级模式**：工具不可用（MCP 断开、HTTP 超时）→ 标注 `[⚠️ Tool verification skipped — <reason>]`，以 LLM-only verdict 继续，不阻塞。

---

## 门禁执行流程

```
Agent 产出
    │
    ▼
┌──────────────────┐
│ 是 Pattern A？    │──YES──→ 执行 A1-A3 检查
└──────┬───────────┘
       │ NO
       ▼
┌──────────────────┐
│ 是 Pattern B？    │──YES──→ 执行 B1-B4 检查
└──────┬───────────┘
       │ NO
       ▼
   跳过本门禁
```

---

## 确认标记

| 结果 | 标记 |
|------|------|
| Pattern A Gate 通过 | `[Cross-Validation Gate: Pattern A PASS]` |
| Pattern B Gate 通过 | `[Cross-Validation Gate: Pattern B PASS]` |
| 降级交付 | `[Cross-Validation Gate: DEGRADED — <原因>]` |
| 跳过（未启用） | 无需标记 |

---

## 与现有质量门禁的关系

本门禁**补充**而非替代以下门禁：
- **De-AI-Fier Gate**（`instructions/de-ai-fier-gate.instructions.md`）：AI 语调与术语检查
- **Pre-Delivery Audit**（`instructions/pre-delivery-audit.instructions.md`）：物理合理性审核

执行顺序：De-AI-Fier Gate → Cross-Validation Gate → Pre-Delivery Audit → 交付
