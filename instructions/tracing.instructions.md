---
description: "Agent 执行追踪规范：span-tree JSONL schema、SQLite 查询工具、decision_rationale + routing_path 字段。"
version: 1
revision: 1
applyTo: "task-executor, plan-architect, claim-verifier, critical-thinking, data-analyst, diagram-architect, dify-kb-manager, format-engineer, ip-protection-advisor, literature-manager, scientific-paper-research, simulation-analyst, simulation-builder, standards-navigator, teaching-assistant, upwork-proposal, bilingual-polisher"
---

# Agent Tracing — Span-Tree 追踪

## JSONL Schema

每行一个 JSON object，存储在 `traces/trace.jsonl` (repo root)，append-only。

### 完整 Span 结构

```json
{
  "trace_id": "01JG7X2Y8Z0000000000000000",
  "parent_span_id": null,
  "span_id": "01JG7X2Y8Z0000000000000001",
  "agent_name": "task-executor",
  "model": null,
  "task_description": "Execute plan: fleet-priority1-upgrade",
  "status": "STARTED",
  "error_type": null,
  "duration_ms": null,
  "token_usage": null,
  "decision_rationale": null,
  "routing_path": null,
  "timestamp": "2026-07-11T10:30:00.000Z"
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| trace_id | string (UUID7) | ✅ | 一次 user request 的全局 trace id，root span 的 span_id 与 trace_id 同值 |
| parent_span_id | string (UUID7) \| null | ✅ | 父 span id；root span 填 null |
| span_id | string (UUID7) | ✅ | 当前 span 的唯一 id |
| agent_name | string | ✅ | 执行 agent 名（如 `task-executor`、`academic-writer`） |
| model | string \| null | ⬜ | 使用的模型 id（如 `fallback/deepseek-v4-pro`），TE 自身 span 可为 null |
| task_description | string | ✅ | task 描述，≤200 chars |
| status | enum | ✅ | `STARTED` \| `SUCCESS` \| `FAILED` \| `BLOCKED` \| `SKIPPED` |
| error_type | enum \| null | ⬜ | 仅当 status 非 SUCCESS 时填写：`ambiguity` \| `test_failure` \| `dependency_failure` \| `agent_unavailable` \| `mcp_unavailable` \| `env_error` \| `timeout` \| `cost_budget` |
| duration_ms | int \| null | ⬜ | wall-clock 耗时毫秒（从 STARTED 到 SUCCESS/FAILED 的时间差） |
| token_usage | {input,output,reasoning} \| null | ⬜ | 仅当子 agent 返回 token header 时填写 |
| decision_rationale | string \| null | ⬜ | TE 的 Domain Detection 路由决策理由（≤500 chars）——为何选此 agent 而非候选。仅 TE 的 per-task STARTED span 填写 |
| routing_path | string \| null | ⬜ | Domain Detection 匹配路径，如 `priority 2 → simulation-builder (MCNP input detected)` |
| timestamp | string (ISO8601) | ✅ | span 开始时间（`date -u +%Y-%m-%dT%H:%M:%SZ`） |

### 写入规则

1. **root span**: Task Executor 在开始执行 plan 时写一行，`parent_span_id=null`，`span_id=trace_id`，`status=STARTED`
2. **root span 完成**: TE 在全部任务完成后写第二行 root span，`status=SUCCESS|PARTIAL|FAILED|HALTED`，补全 `duration_ms`
3. **child span (STARTED)**: TE 在每次 `opencode task(...)` 调用前写一行 `status=STARTED`
4. **child span (完成)**: TE 在子 agent 返回后写一行 `status=SUCCESS|FAILED|BLOCKED`，包含 `duration_ms` 和 `error_type`
5. TE 从子 agent return text 解析 token header：`[TOKENS: in=NNN, out=NNN, reason=NNN]`，填入 `token_usage`

### 存储位置

`traces/trace.jsonl` (repo root)。每次 session 追加写入，不截断。

### Span Tree 示例

对一个 plan 执行过程，完整 trace：

```jsonl
{"trace_id":"01JG01","span_id":"01JG01","parent_span_id":null,"agent_name":"task-executor","model":null,"task_description":"Execute plan: demo","status":"STARTED","timestamp":"2026-07-11T10:00:00Z"}
{"trace_id":"01JG01","span_id":"01JG02","parent_span_id":"01JG01","agent_name":"academic-writer","model":"fallback/deepseek-v4-pro","task_description":"Execute T1.1: Write abstract","status":"STARTED","timestamp":"2026-07-11T10:00:05Z"}
{"trace_id":"01JG01","span_id":"01JG02","parent_span_id":"01JG01","agent_name":"academic-writer","model":"fallback/deepseek-v4-pro","task_description":"Execute T1.1: Write abstract","status":"SUCCESS","duration_ms":12345,"token_usage":{"input":1234,"output":567,"reasoning":89},"timestamp":"2026-07-11T10:00:17Z"}
{"trace_id":"01JG01","span_id":"01JG03","parent_span_id":"01JG01","agent_name":"data-analyst","model":"fallback/deepseek-v4-pro","task_description":"Execute T1.2: Analyze data","status":"STARTED","timestamp":"2026-07-11T10:00:20Z"}
{"trace_id":"01JG01","span_id":"01JG03","parent_span_id":"01JG01","agent_name":"data-analyst","model":"fallback/deepseek-v4-pro","task_description":"Execute T1.2: Analyze data","status":"FAILED","error_type":"test_failure","duration_ms":8900,"token_usage":{"input":2000,"output":300,"reasoning":150},"timestamp":"2026-07-11T10:00:29Z"}
{"trace_id":"01JG01","span_id":"01JG01","parent_span_id":null,"agent_name":"task-executor","model":null,"task_description":"Execute plan: demo","status":"PARTIAL","duration_ms":35000,"timestamp":"2026-07-11T10:00:35Z"}
{"trace_id":"01JG01","span_id":"01JG04","parent_span_id":"01JG01","agent_name":"task-executor","model":null,"task_description":"Execute T1.3: Run MCNP simulation","status":"STARTED","decision_rationale":"priority 2 match: task mentions MCNP input deck and SDEF card → simulation-builder is only agent with MCNP code generation authority","routing_path":"priority 2 → simulation-builder","timestamp":"2026-07-12T10:00:00Z"}
```
