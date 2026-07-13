---
name: "pm-excel-task-sync"
description: "Synchronize Excel task progress with project-management PM system using safe diff, PM Coordinator writes, read-back verification. Excel任务表同步, PM任务对比, 项目管理, 任务更新, 任务补充, 归档标签, 去重核查, TRITIUM-CYCLE, 半自动同步流程."
revision: 1
---

# PM Excel Task Sync

> Crystallized from: 2026-05-26 TRITIUM-CYCLE Excel task progress import, PM diff, safe update/create/archive-tag workflow.
> Date: 2026-05-26
> Trigger: T3 — user explicitly requested crystallization into a reusable Skill.

## When to Use

- The user provides a new Excel task-management workbook and asks to compare it with the project-management PM system.
- The task is to semi-automatically update PM tasks from a table while avoiding accidental deletes, duplicate creates, or wrong fuzzy matches.
- The workbook has task-like columns such as title, assignee, due date, progress/status, latest record, dependencies, notes, or similar Chinese fields: `任务描述`, `任务执行人`, `预计完成`, `进度`, `最新进展记录`, `关联：前置/依赖`, `备注`.
- The project is managed through `project-management/*` tools and PM writes must go through the `PM Coordinator` subagent.
- The desired output includes a human-readable diff report, a structured execution plan, safe PM write batches, and read-back verification.

## When NOT to Use

- The user only wants a one-off summary of the Excel file with no PM comparison or PM update.
- The data source is not task/progress data, such as budget tables, publication metadata, or simulation results.
- The user asks to directly overwrite the PM database, bulk delete tasks, or bypass PM Coordinator classification rules.
- The PM project cannot be identified and the user has not supplied enough project keywords to safely match it.
- The workflow requires editing MCP server internals or PM database files directly; use PM tools only.

## Workflow

1. **Confirm scope and create a todo list**
   - Identify the Excel path, target PM project code/name, and whether the user authorizes writes.
   - If writes are not explicitly requested, stop after producing the diff report.
   - Track at least: extract Excel, read PM tasks, diff/match, prepare execution plan, execute writes, read-back verify.

2. **Extract the Excel workbook to JSON**
   - Use Python `openpyxl` locally for workbook inspection and extraction.
   - Inspect sheets first: names, row counts, column headers, and a few sample rows.
   - Convert the main task sheet to a stable JSON file, usually under `/tmp/<project>_excel_tasks.json`.
   - Preserve row numbers and original text fields for traceability.

   Typical normalized fields:
   - `row`
   - `title`
   - `start`
   - `due`
   - `completed`
   - `delay_flag`
   - `assignee`
   - `priority`
   - `progress`
   - `latest_record`
   - `dependencies`
   - `type`
   - `okr`
   - `notes`

3. **Read PM task data through PM Coordinator**
   - For project-management writes or classification-sensitive operations, always delegate to `PM Coordinator`.
   - Ask PM Coordinator to identify the project, retrieve all tasks, and export/read full task details if available.
   - If direct read-only tools are used, do not pass placeholder optional values like `project_id=0`; that can behave as an exact filter and return no tasks.
   - Save/read a PM task JSON snapshot such as `/tmp/<project>_pm_tasks.json` for local diffing and rollback reference.

4. **Build a conservative diff**
   - Match by exact normalized title first.
   - Then match by compact-normalized title: full/half width normalization, whitespace removal, punctuation and dash unification, case normalization.
   - Use fuzzy matching only with a high threshold and a manual review list.
   - Score candidates using assignee, status, due date, and source tags; never trust title similarity alone.

   Recommended status mapping:
   - Excel `已完成` → PM `done`
   - Excel `进行中` → PM `doing`
   - Excel `未开始` → PM `todo`
   - Excel `已停滞` → PM `blocked`

   Produce at least four categories:
   - A. Excel-only: candidate creates, grouped by active vs completed.
   - B. Matched but different: candidate updates for status, assignee, due, notes/latest record, dependencies.
   - C. PM-only: classify as keep, verify-complete, verify-duplicate/archive, or archive-candidate.
   - D. Duplicate/similar tasks: Excel internal duplicates, PM internal duplicates, fuzzy cross-system matches.

5. **Create a human-readable report and structured execution plan**
   - Write a Markdown report such as `/tmp/<project>_diff_report.md`.
   - Write a JSON execution plan such as `/tmp/<project>_pm_execution_plan.json`.
   - Separate safe updates from ambiguous matches.
   - Highlight dangerous fuzzy matches for manual correction before write batches.

6. **Safety-review ambiguous matches before writes**
   - Check title suffixes, assignees, and due dates for any fuzzy match.
   - Example from source task: HWS-18 tasks had shared base titles but different assignee suffixes; a naive fuzzy match would have reassigned the wrong people.
   - Example from source task: `Aspen模拟：...` titles matched PM tasks without the prefix and should update existing tasks, not create duplicates.
   - Example from source task: `comsol 6.2安装` matched an existing suffixed task `comsol 6.2安装-邱岩`; tag it as possible suffix mismatch instead of duplicating blindly.

7. **Execute PM writes in batches through PM Coordinator**
   - Batch 1: update active matched differences first, especially `status`, `assignee`, and `due`.
   - Batch 2: create Excel-only active tasks after deduplication; map near-duplicates to existing PM tasks with review tags instead of creating duplicates.
   - Batch 3: classify PM-only active tasks by tags and notes only; do not delete, cancel, or mark done automatically.
   - Batch 4: mark duplicate candidates with review tags; do not merge automatically.
   - Batch 5: tag PM-only done tasks as archive candidates; keep audit trail.

   Useful tags:
   - `sync:excel-YYYY-MM-DD`
   - `source:excel:YYYY-MM-DD`
   - `sheet:<sheet-name>`
   - `excel-row:<row>`
   - `excel-status:<mapped-status>`
   - `not-in-YYYY-MM-DD-excel`
   - `archive-candidate:pm-only-done`
   - `pm-review:verify-complete`
   - `pm-review:pm-new-keep`
   - `pm-review:high-value-output`
   - `pm-review:model-dev`
   - `pm-review:excel-missing-keep`
   - `pm-review:verify-duplicate-or-archive`
   - `pm-review:duplicate-candidate`
   - `pm-review:verify-new-stage-or-close`

8. **Preserve notes carefully**
   - Treat PM notes updates as full replacements unless the tool explicitly supports append.
   - Before adding notes, read existing notes, append locally, then write the full content back.
   - For long notes, keep a pre-write PM JSON snapshot. If a tool truncates or summarizes notes, restore from the snapshot immediately.

9. **Read back and verify**
   - Ask PM Coordinator to verify key updated fields, newly created tasks, tags, and sampled archive/duplicate markings.
   - Verify counts: created tasks, updated tasks, tasks tagged with `sync:excel-YYYY-MM-DD`, and project status distribution.
   - If any limitation appears, report it explicitly and create a follow-up item instead of pretending it succeeded.

10. **Summarize changes and follow-ups**
    - Report exactly what was updated, created, tagged, skipped, or partially failed.
    - Emphasize that no tasks were deleted unless the user explicitly requested and PM Coordinator confirmed safe deletion.
    - List follow-ups such as unsupported priority changes or review tags needing human confirmation.

## Inputs & Outputs

| Input | Source |
|-------|--------|
| Excel workbook path | User-provided local path, e.g. `/home/gw/Downloads/...xlsx` |
| Target PM project | User request, workspace context, or PM Coordinator project detection |
| Excel task sheet name | Workbook inspection, often `任务管理` |
| PM task snapshot | PM Coordinator read/export result |
| Write authorization | Explicit user request to update/create/tag PM tasks |

| Output | Format |
|--------|--------|
| Excel extraction | JSON, e.g. `/tmp/<project>_excel_tasks.json` |
| PM snapshot | JSON, e.g. `/tmp/<project>_pm_tasks.json` |
| Diff report | Markdown, e.g. `/tmp/<project>_diff_report.md` |
| Execution plan | JSON and/or Markdown, e.g. `/tmp/<project>_pm_execution_plan.json` |
| PM changes | PM tasks updated/created/tagged through PM Coordinator |
| Verification report | Markdown summary with read-back status |

## Common Pitfalls

- **Placeholder optional filters can hide all PM tasks.** Passing `project_id=0` to task-list tools may act like an exact filter and return zero results. Omit unavailable optional fields or delegate reads to PM Coordinator.
- **Fuzzy matching can swap assignees.** Shared base titles with suffixes such as `-蒋应伍`, `-兰彦`, `-DIV`, `-TCAP` must be manually checked before updating assignee or status.
- **Prefix/suffix differences should not always create new tasks.** Titles like `Aspen模拟：Aspen 进行TCAP流程性模拟` may already exist as `Aspen 进行TCAP流程性模拟`; map and tag instead of duplicating.
- **Do not delete PM-only tasks.** PM-only often means Excel omitted newer high-value tasks. Classify with tags such as `pm-review:pm-new-keep` or `pm-review:verify-complete`.
- **Done tasks should keep audit trail.** For PM-only done tasks, prefer `not-in-YYYY-MM-DD-excel` and `archive-candidate:pm-only-done` tags over physical deletion.
- **PM notes may be full-replace.** Always read existing notes, append locally, and write back full notes. Keep a pre-sync PM snapshot to restore long notes if a tool truncates them.
- **Priority updates may be unsupported.** In the source task, `pm_task_update` could not modify `priority`; report partial success and leave a follow-up.
- **Repeated titles with different assignees may be intentional sub-tasks.** For multi-person review/check tasks, keep separate tasks and rely on assignee/tags to distinguish them.
- **PM writes must go through PM Coordinator.** Never call PM write tools directly from a general agent.

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-05-26 | Initial crystallization of Excel-to-PM diff/sync workflow with safe matching, PM Coordinator writes, tags, duplicate review, archive marking, and read-back verification. | TRITIUM-CYCLE task progress Excel sync on 2026-05-26 |
