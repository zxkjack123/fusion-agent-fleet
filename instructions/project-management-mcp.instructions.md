---
description: "Project management policy: read/query PM operations may be called directly; write/classify operations MUST delegate to PM Coordinator subagent. PM Coordinator is the single source of truth for task/schedule classification, cross-project queries, and conflict detection."
applyTo: "**"
revision: 3
---

# Project Management MCP Policy — PM Coordinator Delegation

PM operations are split into two tiers: **read/query operations** may be called directly by any agent that has them in its `tools:` list; **write/classify operations** MUST delegate to the **PM Coordinator** subagent.

## Core Rule

> **Self-Exclusion**: This instruction does NOT apply to the **PM Coordinator** agent itself. PM Coordinator is the ONLY agent authorized to directly call ALL `project-management/*` MCP tools (both read and write). The tiered delegation requirement below applies exclusively to all OTHER agents.

> **Read/query operations** (see Operation Mapping below): May be called directly if the tool is in your `tools:` list. No delegation needed.
>
> **Write/classify operations** (see Operation Mapping below): MUST delegate to PM Coordinator via `opencode task`. Do not call these tools directly.

## Why PM Coordinator Instead of Direct Calls

| 风险 | 直接调用 | PM Coordinator |
|------|---------|---------------|
| 会议被误写成 task | ❌ agent 自行判断 | ✅ PM Coordinator 强制分类 |
| 跨项目查询失败 | ❌ 默认检测当前项目 | ✅ PM Coordinator 明确处理 project_code |
| 日程查不到 | ❌ 用 task_list 查日程 | ✅ 用 schedule_list 查询 |
| 信息存成 done task | ❌ 无分类规则 | ✅ 强制分流到 important_info |
| 重复条目 | ❌ 无去重 | ✅ 写入前查询 |
| 工具选择错误 | ❌ 每个 agent 各自判断 | ✅ 集中路由逻辑 |

## Operation Mapping — 分级委派

### May Call Directly (✅ Read/Query)

These are **read-only operations** with no classification, dedup, or conflict-detection needs. Any agent with the tool in its `tools:` list may call directly.

| You want to... | Use this tool directly |
|----------------|----------------------|
| Get task details | `pm_task_get` |
| List/filter tasks | `pm_task_list` |
| Check task blocking (upstream) | `pm_task_get_blocking` |
| Check tasks blocked by (downstream) | `pm_task_list_blocked_by` |
| List schedules | `pm_schedule_list` |
| List people | `pm_people_list` |
| Get person details | `pm_people_get` |
| Check person workload | `pm_people_workload` |
| List person affiliations | `pm_people_affiliations_list` |
| List person education | `pm_people_education_list` |
| List projects | `pm_projects_list` |
| Detect current project | `pm_detect_project` |
| List project locations | `pm_project_list_locations` |
| Get project context rules | `pm_project_context_rules_get` |
| Project analytics | `pm_analytics_project` |
| Person analytics | `pm_analytics_person` |
| Week-ahead risk | `pm_week_ahead_risk` |
| List important info | `pm_important_info_list` |
| Asset version history | `pm_asset_history` |
| Asset snapshot (read) | `pm_asset_snapshot` |
| List communications | `pm_comm_list` |
| List planner runs | `pm_planner_plan_runs_list` |
| Get planner run details | `pm_planner_plan_run_get` |
| Export graph | `pm_graph_export` |
| Export stream | `pm_export_stream` |
| Export dependency graph | `pm_dependency_graph_export` |
| Find similar tasks | `pm_similar_tasks` |
| Graph path QA | `pm_graph_path_qa` |
| Search PM tools | `pm_tools_search` |

### Must Delegate to PM Coordinator (🔄 Write/Classify)

These operations involve **creating, updating, deleting, classifying, or triggering side-effects**. They MUST go through PM Coordinator for intent classification, dedup, conflict detection, and verification read-back.

| You want to... | Delegate to PM Coordinator | NOT this |
|----------------|---------------------------|----------|
| Create a task | `opencode task("PM Coordinator")` | `pm_task_create` directly |
| Update a task | `opencode task("PM Coordinator")` | `pm_task_update` directly |
| Complete a task | `opencode task("PM Coordinator")` | `pm_task_complete` directly |
| Set task dependencies (full replace) | `opencode task("PM Coordinator")` | `pm_task_set_dependencies` directly |
| Add task dependency | `opencode task("PM Coordinator")` | `pm_task_add_dependency` directly |
| Remove task dependency | `opencode task("PM Coordinator")` | `pm_task_remove_dependency` directly |
| Add schedule/meeting | `opencode task("PM Coordinator")` | `pm_schedule_add` directly |
| Delete schedule | `opencode task("PM Coordinator")` | `pm_schedule_delete` directly |
| Add person | `opencode task("PM Coordinator")` | `pm_people_add` directly |
| Update person | `opencode task("PM Coordinator")` | `pm_people_update` directly |
| Set person affiliations | `opencode task("PM Coordinator")` | `pm_people_affiliations_set` directly |
| Add education record | `opencode task("PM Coordinator")` | `pm_people_education_add` directly |
| Initialize project | `opencode task("PM Coordinator")` | `pm_project_init` directly |
| Smart-init project | `opencode task("PM Coordinator")` | `pm_project_smart_init` directly |
| Add project location | `opencode task("PM Coordinator")` | `pm_project_add_location` directly |
| Set project context rules | `opencode task("PM Coordinator")` | `pm_project_context_rules_set` directly |
| Policy check (planner) | `opencode task("PM Coordinator")` | `pm_planner_policy_check` directly |
| Plan preview (planner) | `opencode task("PM Coordinator")` | `pm_planner_plan_preview` directly |
| Scan assets (triggers DB write) | `opencode task("PM Coordinator")` | `pm_assets_scan` directly |
| Analyze asset changes | `opencode task("PM Coordinator")` | `pm_assets_analyze` directly |
| Mark asset important | `opencode task("PM Coordinator")` | `pm_asset_mark_important` directly |
| Add important info | `opencode task("PM Coordinator")` | `pm_important_info_add` directly |
| Add communication record | `opencode task("PM Coordinator")` | `pm_comm_add` directly |
| Export communications | `opencode task("PM Coordinator")` | `pm_comm_export` directly |
| Send notification | `opencode task("PM Coordinator")` | `pm_notify` directly |
| Recommend assignments | `opencode task("PM Coordinator")` | `pm_recommend_assignments` directly |

## Agent Integration

1. Ensure `PM Coordinator` is in your agent's `agents:` list.
2. For **read/query operations**: add the needed `project-management/*` tools to your agent's `tools:` list and call them directly.
3. For **write/classify operations**: delegate to PM Coordinator via `opencode task`. In your delegation prompt, specify: operation intent, key parameters, project context.
4. PM Coordinator returns structured results with conflict warnings.

## Tool Categories (for reference only — do NOT call directly)

| 类别 | 工具前缀 | 用途 |
|------|---------|------|
| 任务管理 | `pm_task_*` | 工作任务 CRUD、依赖、状态 |
| 日程管理 | `pm_schedule_*` | 会议/活动日历 |
| 人员管理 | `pm_people_*` | 人员信息、工作量、单位、教育 |
| 项目管理 | `pm_project_*` | 项目初始化、配置、位置 |
| 计划管理 | `pm_planner_*` | 执行计划运行、策略检查 |
| 资产 | `pm_assets_*` | 文件资产追踪、快照、历史 |
| 信息 | `pm_important_info_*` | 设计基线/关键参数 |
| 沟通 | `pm_comm_*` | 沟通记录 |
| 分析 | `pm_analytics_*`, `pm_week_ahead_risk`, `pm_recommend_assignments` | 项目/人员统计 |
| 图谱 | `pm_graph_*`, `pm_export_*`, `pm_dependency_graph_export` | 知识图谱导出 |
| 检索 | `pm_similar_tasks`, `pm_graph_path_qa`, `pm_tools_search` | 语义检索 |
| 通知 | `pm_notify` | 微信/邮件推送 |

## Task vs Schedule 判断（参考）

| 用户意图 | PM Coordinator 使用 | 判断依据 |
|----------|-------------------|---------|
| 可执行工作项（有负责人、有完成标准） | `pm_task_create` | 关键词：做、完成、提交、开发、修复 |
| 会议/活动/日程安排（有时间、地点、参与人） | `pm_schedule_add` | 关键词：会议、评审、答辩、汇报、日程；或含精确时刻 HH:MM |
| 混合场景（会议 + 会前准备任务） | 两者都用 | 会议 → `pm_schedule_add`；准备工作 → `pm_task_create` |
| 信息/知识/基线/约定 | `pm_important_info_add` | 非可执行项，仅供查阅 |

## PM Coordinator Failure Detection

When delegating to PM Coordinator via `opencode task`, check the returned response for these failure patterns:

| Failure Pattern | Detection | Action |
|----------------|-----------|--------|
| **Fake tool-call** | Response contains JSON code blocks with `"tool":` keys (e.g., `{"tool": "pm_task_list", ...}`) instead of actual tool results | (1) Retry delegation once with a simplified prompt; (2) if retry also fails, fall back to direct read-only tool calls and annotate `⚠️ PM Coordinator unavailable — direct fallback used` |
| **Empty/truncated response** | Response is empty, contains only whitespace, or ends mid-sentence without a `**Status**:` line | Treat as failure — fall back to direct read-only tool calls for the current operation |
| **No response (hang)** | `opencode task` does not return within the conversation turn | Cannot be detected at instructions level (runtime limitation); if the turn completes without PM Coordinator output, skip PM operations and proceed with core task |

**After any PM Coordinator failure**: Read/query operations from the "May Call Directly" list are still available for direct use. Write/classify operations should be reported as skipped (`⚠️ PM write operation skipped — Coordinator unavailable`) and the agent should proceed with its core task without blocking.

## MCP Unavailable Fallback

If the `project-management` MCP server is unavailable or `PM Coordinator` subagent fails to respond:

1. **Do NOT block the workflow indefinitely.** PM status updates are supplementary — core task execution takes priority.
2. Report to user: `⚠️ PM Coordinator is unavailable. PM operations skipped.`
3. For agents with read/query PM tools in their `tools:` list: these tools may still be attempted directly. If they also fail (MCP server down), skip and proceed.
4. For write/classify operations: skip entirely. Do not attempt to call write tools directly as a workaround — this bypasses Coordinator's classification, dedup, and conflict detection.
5. Record the skipped PM operation in task notes or commit message (e.g., `[PM: skipped]`) for later manual reconciliation.
