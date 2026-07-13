---
description: "统一 State Manager API：整合 checkpoint、span trace、findings ledger、session-memory、Dify KB 五个状态后端的规范化读写接口。"
version: 1
revision: 1
applyTo: "task-executor"
---

# State API — 统一状态管理接口

Task Executor 在执行过程中产生和消费 5 类状态：plan/task 执行记录（checkpoint）、span 追踪（trace.jsonl/trace.db）、发现记录（findings YAML ledger + Dify KB）、session 记忆（session-memory MCP）、跨 session 知识查询（Dify KB semantic search）。

当前这些状态分散在各自的机制中，写入和读取均需要知道具体的后端文件路径/API。本规范定义统一的接口，TE 通过 `scripts/state_api.py` 调用。

## 架构

```
Task Executor
  ├─ state_api.py --mode write_checkpoint  → traces/checkpoint.json + traces/trace.jsonl
  ├─ state_api.py --mode read_checkpoint   → traces/checkpoint.json (JSONL parse)
  ├─ state_api.py --mode is_completed      → traces/checkpoint.json (task status check)
  ├─ state_api.py --mode extract_claims    → stdin text → JSON claims (regex + heuristic)
  ├─ state_api.py --mode write_finding     → projects/<project>/findings/<YYYYMMDD>-<seq>.yaml
  └─ state_api.py --mode query_span        → traces/trace.db (via trace_query.py)
```

## 四个 Scope / 七个操作

### plan_task scope — `traces/checkpoint.json`

**Backend**: JSONL append-only file。每行一条 checkpoint 记录。

**操作**:

- `write_checkpoint(plan, task_id, trace_id, status, git_commit, files_modified, tokens, duration_ms, error_compact=None)`
  - 追加一行到 `traces/checkpoint.json`
  - 同时可选写入对应的 span entry 到 `traces/trace.jsonl`
  - CLI: `python3 scripts/state_api.py --mode write_checkpoint --plan <name> --task-id <id> --trace-id <id> --status <s> --git-commit <hash> --files '[f1,f2]' --duration-ms <n> [--error-compact 'json']`

- `read_checkpoint(plan, task_id=None)`
  - 读取指定 plan 的所有已完成 task 列表，或按 task_id 过滤
  - CLI: `python3 scripts/state_api.py --mode read_checkpoint --plan <name> [--task-id <id>]`

- `is_completed(plan, task_id)`
  - 快速判断任务是否已完成
  - CLI: `python3 scripts/state_api.py --mode is_completed --plan <name> --task-id <id>`

### span scope — `traces/trace.jsonl` / `traces/trace.db`

**Backend**: `trace_query.py` SQLite 索引（必须先 `python3 scripts/trace_query.py --ingest`）。

**操作**:

- `query_span(trace_id)`
  - 查询指定 trace 的完整 span 树
  - CLI: `python3 scripts/state_api.py --mode query_span --trace-id <id>`

### session scope — `session-memory MCP`

**Backend**: session-memory MCP server。操作通过 MCP tool 委托，不在 `state_api.py` 中实现。

**操作**（由 TE 通过 MCP 调用）:

- `memory_search(query)` — 搜索历史 session
- `memory_recall(task_description)` — 召回相关上下文
- `memory_ingest()` — 索引当前 session

### cross-session scope — findings YAML + Dify KB

**Backend**: `projects/<project>/findings/` (YAML file ledger) + Dify KB (semantic search, `project-<project>-findings` dataset)。

**操作**:

- `write_finding(project, finding_dict)`
  - 写入 YAML 文件（`projects/<project>/findings/<YYYYMMDD>-<seq>.yaml`）
  - 不直接写入 Dify KB——Dify KB 写入由 `dify-kb-manager` agent 处理（TE 在 Post-Completion Step 2 中委派）
  - CLI: `python3 scripts/state_api.py --mode write_finding --project <name> --finding 'json_dict'`

- `extract_claims(text)`
  - 从 agent 输出文本中自动提取数值声明
  - 匹配模式：`<value> ± <uncertainty> <unit>` + 验证关键词（CONFIRMED, within 1σ, matches literature）
  - 输出：`[{value, uncertainty, unit, context, verdict}]`
  - CLI: `echo "$OUTPUT" | python3 scripts/state_api.py --mode extract_claims`

## TaskResult Schema

```python
@dataclass
class TaskResult:
    task_id: str
    plan: str
    trace_id: str
    status: str        # COMPLETED | FAILED | BLOCKED
    git_commit: str
    files_modified: list[str]
    error_compact: dict | None
    claims: list[dict]       # auto-extracted quantitative claims
    tokens: dict | None      # {input, output, reasoning}
    duration_ms: int
```

## ClaimRecord Schema

```python
@dataclass
class ClaimRecord:
    value: float
    uncertainty: float | None
    unit: str
    context: str        # surrounding sentence (≤200 chars)
    verdict: str        # CONFIRMED | CONTRADICTED | UNVERIFIED
```

## 幂等性保证

- `write_checkpoint`: 检查同 `(plan, task_id)` 是否已存在 COMPLETED 记录。若已存在，skip（不重复写入）。
- `write_finding`: 按 `<YYYYMMDD>-<seq>` 自增序列号，天然幂等。
- `is_completed`: 只读操作，天然幂等。

## 错误处理

- checkpoint.json 不存在 → 返回空列表（针对 read/is_completed）
- trace.db 不存在 → 返回 `{"error": "trace db not found, run trace_query.py --ingest first"}`
- 文件写入权限不足 → 打印错误并 exit 1
