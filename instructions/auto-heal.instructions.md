---
description: "Task Executor 3 轮 LLM 驱动自动修复循环（auto-heal loop）的完整规范。Diagnose → Fix → Re-test 循环。"
version: 1
revision: 1
applyTo: "task-executor"
---

# Auto-Heal — LLM-Driven Error Fix Loop

## 触发条件

Task Executor 在以下场景触发 auto-heal loop：
1. 测试失败（停止条件 #2）：Path A/B 手动修复已尝试但仍失败 → 进入 auto-heal
2. 可选：用户显式传 `--auto-fix` 标志

## Auto-Heal Loop（3 轮）

每轮执行步骤：

1. **Diagnose**: 收集当前 task 的 error 信息：
   - `## Execution Log` 中本 task 的最新 JSON block (error_type, summary, root_cause_guess)
   - 测试命令的完整输出 (stdout + stderr)
   - 涉及的源文件路径列表 (affected_files)
2. **Prepare context for deep-reviewer**: 将 error info 写入临时 review context 文件（deep-reviewer 的 inbound contract 期望 `target_files: [list of paths]`）：
   ```bash
   cat > .agent-runs/auto-heal-context-<task_id>.md << 'AUTOHEAL_EOF'
   # Auto-Heal Context: <task_id>
   ## Error Info
   <error_type + summary + root_cause_guess from Execution Log JSON>
   ## Test Command
   <test_commands>
   ## Full Output
   <full_error_output>
   ## Affected Source Files
   <list of paths>
   AUTOHEAL_EOF
   ```
3. **Delegate to deep-reviewer**: 委派 deep-reviewer 分析错误并生成修复方案。按 deep-reviewer 的 inbound contract（`.opencode/agent/deep-reviewer.md` `### 调用方需提供`）传递字段：
   ```
   opencode task(subagent_type="deep-reviewer",
     prompt="Review the following test failure and generate a concrete code fix.
     target_files: ['<affected_files>', '.agent-runs/auto-heal-context-<task_id>.md']
     mode: deep
     focus_areas: ['error_diagnosis','code_fix']
     severity_floor: error
     
     The context file (.agent-runs/auto-heal-context-<task_id>.md) contains the error log and test command output.
     Analyze the error, identify the root cause, and provide:
     (a) root cause analysis with file:line references,
     (b) exact code changes needed (edit commands or unified diff),
     (c) the verification command to re-run."
   )
   ```
4. **Apply fix**: TE 根据 deep-reviewer 的 fix suggestion，使用 `edit` 工具修改源文件
5. **Re-test**: 重新运行原 task 的 `test_commands`
6. **判定**:
   - test 通过 → 标记 task `✅`，退出 auto-heal loop，记录 span `status=SUCCESS, decision_rationale="auto-heal round <N> fixed with deep-reviewer"`
   - test 仍失败 → 进入下一轮（最多 3 轮）
   - 达到 3 轮上限 → 标记 task `❌ FAILED`，写入 Execution Log（含 auto-heal 每轮的 fix attempt details）

## 收敛 / 放弃条件

| 条件 | 行为 |
|------|------|
| 3 轮 auto-heal 后 test 仍失败 | 放弃，标记 FAILED |
| deep-reviewer 不可用 | 降级使用 Plan Architect mode=improve 作为 fallback |
| deep-reviewer 连续 2 轮返回相同 fix (未收敛) | 提前放弃，标记 FAILED |
| 任何一轮的 fix 引入了新错误（regression） | 回滚该轮 patch，进入下一轮 |

## 与现有停止条件的关系

- Auto-heal 是停止条件 #2 的**扩展**——在 "≥2 条手动 Path A/B 修复" 之后、"报告 FAILED" 之前
- 总尝试次数上限：Path A + Path B + 3 轮 auto-heal = 5（不变）
- Auto-heal 不影响条件 #1 (成功)、#3 (歧义)、#4 (依赖传播)

## Span Tracing

Auto-heal 的每轮 repair attempt 作为当前 task span 的 child span 记录：
```bash
echo '{"trace_id":"'$ROOT_TRACE_ID'","span_id":"'$(python3 -c "import uuid; print(uuid.uuid7())")'","parent_span_id":"'$SPAN_ID'","agent_name":"deep-reviewer","model":"<model>","task_description":"Auto-heal round <N>: fix <task_id>","status":"<SUCCESS|FAILED>","decision_rationale":"auto-heal fix attempt round <N>","duration_ms":<ms>,"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' >> traces/trace.jsonl
```
