---
description: "Task Executor 持久化执行规范：checkpoint.write → resume.skip → autoclean.on_plan_end 完整生命周期。"
version: 1
revision: 1
applyTo: "task-executor"
---

# Durable Execution — Task Checkpoint / Resume

## Schema

每行一个 JSON object，存储在 `traces/checkpoint.json`。

```json
{
  "plan": "fleet-priority1-upgrade",
  "task_id": "T2.3",
  "trace_id": "01JG7X2Y8Z",
  "status": "COMPLETED",
  "git_commit": "abc1234",
  "files_modified": ["src/foo.py"],
  "started_at": "2026-07-12T10:00:00Z",
  "completed_at": "2026-07-12T10:05:30Z",
  "duration_ms": 330000,
  "token_input": 1234,
  "token_output": 567
}
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| plan | ✅ | 计划文件 base name（不含路径和 .md 后缀） |
| task_id | ✅ | Task id（如 "T2.3"） |
| trace_id | ✅ | 当前 session 的 root trace_id |
| status | ✅ | COMPLETED |
| git_commit | ✅ | 该 task 的 commit hash |
| files_modified | ✅ | 该 task 修改的文件列表 |
| started_at | ✅ | task 开始时间 (ISO8601) |
| completed_at | ✅ | task 完成时间 |
| duration_ms | ✅ | 执行耗时 (ms) |
| token_input | ✅ | input token 数 (从 span 记录中获取) |
| token_output | ✅ | output token 数 |

## 写入规则

Task Executor 在每个 task 的 Step 6 (Commit) 完成后，追加一行到 `traces/checkpoint.json`：

```bash
echo '{"plan":"<plan_name>","task_id":"<task_id>","trace_id":"'$ROOT_TRACE_ID'","status":"COMPLETED","git_commit":"<commit>","files_modified":["<files>"],"started_at":"<ISO8601>","completed_at":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","duration_ms":<ms>,"token_input":<N>,"token_output":<M>}' >> traces/checkpoint.json
```

## 恢复规则 (Session Start)

Task Executor 在开始执行 plan 之前，检测 checkpoint：

```bash
if [ -f traces/checkpoint.json ]; then
  # Parse completed task IDs from checkpoint
  python3 -c "
  import json, sys
  with open('traces/checkpoint.json') as f:
      entries = [json.loads(l) for l in f if l.strip()]
  plan_name = '<plan_name>'
  completed = {e['task_id'] for e in entries if e['plan'] == plan_name and e['status'] == 'COMPLETED'}
  if completed:
      print(f'⏭  Skipping {len(completed)} completed task(s): {sorted(completed)}')
  else:
      print('No matching checkpoint entries — starting fresh')
  "
fi
```

TE 在 Step 0 (定位当前任务) 时，如果在 checkpoint 中发现当前 task 已标记 COMPLETED，跳过该 task 并直接进入下一个未完成的 task。

Skip logic:
```
IF task_id IN checkpoint.completed:
  → Mark task as ⏭ SKIPPED (from checkpoint) in plan summary
  → Move to next task
ELSE:
  → Execute task normally
```

## 清理规则

Checkpoint 在 plan 执行完成后自动清理：

```bash
# After plan COMPLETED/HALTED:
python3 -c "
import json
with open('traces/checkpoint.json') as f:
    entries = [json.loads(l) for l in f if l.strip()]
plan_name = '<plan_name>'
others = [json.dumps(e) for e in entries if e['plan'] != plan_name]
if others:
    with open('traces/checkpoint.json', 'w') as f:
        f.write('\n'.join(others) + '\n')
else:
    import os; os.remove('traces/checkpoint.json')
"
```
