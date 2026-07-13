---
description: "Gate Runner 的调用契约：pre-gate 和 post-gate 输入/输出规范、gate 链矩阵、severity escalation rules、调用时机表。"
version: 1
revision: 1
applyTo: "task-executor, fusion-deep-research"
---

# Gate Runner Contract — 调用契约

Gate Runner 是 harness-level 的 pre/post-execution verification agent。调用方（Task Executor 或 Fusion Deep Research）在委派关键 agent 之前/之后显式调用 gate-runner，按 delivery_tier 自动选择 gate 链。

## Pre-Gate 调用

**时机**：委派 target agent 之前。对 `delivery_tier` ∈ {orchestrator, producer-external, producer-internal} 的 agent 触发。

**调用格式**：

```
task(subagent_type="gate-runner",
  prompt="mode=pre
target_agent_name=<name>
target_agent_tier=<orchestrator|producer-external|producer-internal>
Run pre-gate checks per your Gate Chain Matrix.")
```

**输入参数**：
- `target_agent_name` (string, required) — 目标 agent 名称
- `target_agent_tier` (enum, required) — 从 `.opencode/agent/<name>.meta.yaml` 的 `delivery_tier` 字段读取

**返回值**：

```
verdict: PASS | WARN | FAIL | BLOCK
gate_results:
  readiness_check: {status, detail}
  tool_budget_check: {status, detail}  # tier-dependent
  delegation_graph_check: {status, detail}  # orchestrator only
```

**Severity escalation**：

| Pre-Gate Verdict | TE Action |
|-----------------|-----------|
| PASS | 继续委派 target agent |
| WARN | 继续委派，log 到 Execution Log |
| FAIL | 跳过该 task，标记 ⏸ SKIPPED (gate blocked)，写入 Execution Log |
| BLOCK | 跳过该 task，标记 ⏸ SKIPPED (gate blocked)，**立即通知**（与 FAIL 相同但更严重） |

## Post-Gate 调用

**时机**：target agent 返回后。对 `delivery_tier` ∈ {orchestrator, producer-external, producer-internal} 的 agent 触发。

**调用格式**：

```
task(subagent_type="gate-runner",
  prompt="mode=post
target_agent_name=<name>
target_agent_tier=<tier>
agent_output_text=<full text output from target agent>
Run post-gate checks per your Gate Chain Matrix.")
```

**返回值**：

```
verdict: PASS | WARN | FAIL
gate_results:
  <gate_name>: {status, detail}
```

**Severity escalation**：

| Post-Gate Verdict | TE Action |
|------------------|-----------|
| PASS | 接受结果，继续处理 |
| WARN | 接受结果，log 到 Execution Log |
| FAIL | 触发 auto-heal（stop condition #2）。gate-runner 的 detail 作为修复输入 |

## Gate 链矩阵

| Target Agent Tier | Pre-Gate | Post-Gate |
|-------------------|----------|-----------|
| orchestrator | readiness_check, delegation_graph | factcheck_gate, ip_protection_gate |
| producer-external | readiness_check, tool_budget | de_ai_fier_gate, factcheck_gate, pre_delivery_audit(L2) |
| producer-internal | readiness_check, tool_budget | plausibility_check, pre_delivery_audit(L1) |
| specialist | — | — |

## specialist 豁免

`delivery_tier: specialist` 的 agent（如 explore, explore-subagent, figure-analyst 等纯读取/分析 agent）不需要 pre 或 post gate。它们的输出不产生文件变更，且内部已有自己的质量检查逻辑。

## 调用时机表

以下 agent 在 TE 路由表中会被 gate-runner 覆盖（基于 delivery_tier）：

| Target Agent | Tier | Pre | Post |
|-------------|------|-----|------|
| fusion-deep-research | orchestrator | ✅ | ✅ |
| academic-writer | producer-external | ✅ | ✅ |
| bilingual-polisher | producer-external | ✅ | ✅ |
| communication-drafter | producer-external | ✅ | ✅ |
| literature-reviewer | producer-external | ✅ | ✅ |
| paper-reviewer | producer-external | ✅ | ✅ |
| patent-writer | producer-external | ✅ | ✅ |
| presentation-architect | producer-external | ✅ | ✅ |
| proposal-writer | producer-external | ✅ | ✅ |
| review-responder | producer-external | ✅ | ✅ |
| teaching-assistant | producer-external | ✅ | ✅ |
| upwork-proposal | producer-external | ✅ | ✅ |
| background-reviewer | producer-internal | ✅ | ✅ |
| cross-repo-auditor | producer-internal | ✅ | ✅ |
| data-analyst | producer-internal | ✅ | ✅ |
| diagram-architect | producer-internal | ✅ | ✅ |
| dify-kb-manager | producer-internal | ✅ | ✅ |
| doc-maintainer | producer-internal | ✅ | ✅ |
| doublecheck | producer-internal | ✅ | ✅ |
| experiment-tracker | producer-internal | ✅ | ✅ |
| format-engineer | producer-internal | ✅ | ✅ |
| fusion-chain-runner | producer-internal | ✅ | ✅ |
| ip-protection-advisor | producer-internal | ✅ | ✅ |
| literature-manager | producer-internal | ✅ | ✅ |
| memory-distiller | producer-internal | ✅ | ✅ |
| methodology-deep-reviewer | producer-internal | ✅ | ✅ |
| plan-architect | producer-internal | ✅ | ✅ |
| repo-reviewer | producer-internal | ✅ | ✅ |
| scheduler | producer-internal | ✅ | ✅ |
| scientific-paper-research | producer-internal | ✅ | ✅ |
| simulation-analyst | producer-internal | ✅ | ✅ |
| simulation-builder | producer-internal | ✅ | ✅ |
| standards-navigator | producer-internal | ✅ | ✅ |
| task-executor | producer-internal | ✅ | ✅ |
| citation-scanner | specialist | — | — |
| claim-verifier | specialist | — | — |
| critical-thinking | specialist | — | — |
| deep-reviewer | specialist | — | — |
| explore | specialist | — | — |
| figure-analyst | specialist | — | — |
| figure-quality-reviewer | specialist | — | — |
| gate-runner | producer-internal | — | — |
| innovation-reviewer | specialist | — | — |
| pm-coordinator | specialist | — | — |
| prior-art-semantic-reviewer | specialist | — | — |
| scnet-hpc-coordinator | specialist | — | — |
| structure-format-scanner | specialist | — | — |
