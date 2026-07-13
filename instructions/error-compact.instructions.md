---
description: "全局错误压缩传递规范（[ERROR_COMPACT] JSON-in-Markdown envelope），所有 agent 失败时输出的格式契约。"
version: 1
revision: 1
applyTo: "**"
---

# Error Compact — 结构化错误传递规范

## 适用范围

所有 agent 在返回失败状态时，应在 `## Outbound Delegation Schemas` 中声明 `error_compact` 格式，并在实际错误输出中使用该 envelope。

## Schema

```json
{
  "error_id": "err-<YYYYMMDD-HHMM>-<short_task_id>",
  "error_type": "ambiguity|test_failure|dependency_failure|agent_unavailable|mcp_unavailable|env_error|timeout|cost_budget",
  "summary": "<≤200 chars human-readable error summary>",
  "root_cause_guess": "<1-2 sentences, mandatory>",
  "confidence": "HIGH|MEDIUM|LOW",
  "retry_suggestion": "<≤200 chars actionable fix recommendation>",
  "affected_files": ["<path1>"],
  "blocked_downstream": ["<task_id1>"],
  "task_id": "<caller-assigned task id>",
  "attempted_fixes": ["<fix path 1>"],
  "timestamp": "<ISO8601>"
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| error_id | string | ✅ | 全局唯一 id，格式 `err-<YYYYMMDD-HHMM>-<task_id>` |
| error_type | enum | ✅ | 错误分类 |
| summary | string (≤200 chars) | ✅ | 一句话摘要 |
| root_cause_guess | string | ✅ | 1-2 句根因猜测 |
| confidence | enum | ✅ | 对 root_cause_guess 的信心 |
| retry_suggestion | string (≤200 chars) | ✅ | 可操作的修复建议 |
| affected_files | string[] | ⬜ | 涉及的文件路径 |
| blocked_downstream | string[] | ⬜ | 被阻塞的下游 task |
| task_id | string | ✅ | 当前 task id |
| attempted_fixes | string[] | ⬜ | 已尝试的修复路径 |
| timestamp | ISO8601 | ✅ | 错误发生时间 |

## 使用模式

### Pattern A: Task Executor → Execution Log

Task Executor 在 `## Execution Log` 中使用 prose + JSON block 双副本格式（详见 `.opencode/agent/task-executor.md` §执行反馈记录）。

### Pattern B: Sub-agent → Parent agent

Sub-agent 在 return text 末尾嵌入 error compact：

```
[ERROR_COMPACT]
{
  "error_id": "err-20260711-1030-t21",
  "error_type": "agent_unavailable",
  "summary": "PM Coordinator timed out after 120s",
  "root_cause_guess": "PM MCP server unreachable",
  "confidence": "HIGH",
  "retry_suggestion": "Verify PM MCP server connectivity, retry with longer timeout",
  "affected_files": [],
  "blocked_downstream": [],
  "task_id": "T2.1",
  "attempted_fixes": ["retry 1: same timeout", "retry 2: skip PM sync"],
  "timestamp": "2026-07-11T10:30:00Z"
}
[/ERROR_COMPACT]
```

## 与现有协议的关系

- **与 Execution Log 的关系**：Execution Log 的 JSON block 是 error_compact 的严格超集（多了 `git_commit` 等执行上下文字段）
- **与 NEEDS_USER_DECISION 的关系**：正交——NEEDS_USER_DECISION 用于需要用户输入的场景，error_compact 用于不可恢复的失败
- **与 RETURN ENVELOPE 的关系**：error_compact 是 RETURN ENVELOPE 的失败子格式
