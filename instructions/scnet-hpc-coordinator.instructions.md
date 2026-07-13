---
description: "Scnet HPC Coordinator policy: ALL scnetresource-router job lifecycle operations (submit, cancel, download, choose_best, task_*, upload, container_probe, workspace_run, interactive_start, interactive_stop) MUST delegate to Scnet HPC Coordinator subagent — NEVER call these scnetresource-router tools directly. Lightweight read/monitor operations (remote_*, status, job_tail, task_tail, task_poll, task_diagnose, interactive_status) may still be called directly. HPC 作业协调策略：所有 HPC 作业生命周期操作必须委派给 Scnet HPC Coordinator，不得直接调用。轻量读/监控操作可保留直接调用。"
applyTo: "fusion-deep-research,scnet-hpc-coordinator,simulation-analyst,simulation-builder,task-executor"
revision: 7
---

# Scnet HPC Coordinator Policy — HPC 作业生命周期委派策略

> **Single source of truth**: The canonical direct-vs-delegate classification is maintained in
> `scnet_resource/doc/tool_access_policy.yaml` (CI-enforced against the tool metadata registry).
> The tables below are derived summaries for quick reference.

When tasks involve **HPC job lifecycle operations** (submit, cancel, download, cluster selection, task array management, file upload, container probing), you **MUST** delegate to the **Scnet HPC Coordinator** subagent. Do NOT call these `scnetresource-router/*` MCP tools directly.

**Lightweight read/monitor operations** (remote file read, cluster status, job tail, task poll) may still be called directly for efficiency — delegating every `remote_cat` call through a subagent would add unnecessary latency.

## Core Rule

> **Self-Exclusion**: This instruction does NOT apply to the **Scnet HPC Coordinator** agent itself. Scnet HPC Coordinator is the ONLY agent authorized to directly call `scnetresource-router/*` job lifecycle tools. The delegation requirement below applies exclusively to all OTHER agents.

> **Scnet HPC Coordinator is the ONLY entry point for HPC job lifecycle operations.**
>
> Do not call `scnetresource-router/cancel`, `scnetresource-router/choose` (deprecated alias of `choose_best`; will be removed in v0.12.x), `scnetresource-router/choose_best`, `scnetresource-router/container_probe`, `scnetresource-router/download`, `scnetresource-router/submit`, `scnetresource-router/upload`, `scnetresource-router/wait`, `scnetresource-router/task_create_submit` (deprecated alias of `task_create_submit_auto`; will be removed in v0.12.x), `scnetresource-router/task_create_submit_auto`, `scnetresource-router/task_run_auto`, `scnetresource-router/task_run_array` (deprecated alias of `task_run_array_auto`; will be removed in v0.12.x), `scnetresource-router/task_run_array_auto`, `scnetresource-router/task_upload_inputs`, `scnetresource-router/task_download_outputs`, `scnetresource-router/task_array_download`, `scnetresource-router/task_array_retry_failed`, `scnetresource-router/task_import`, `scnetresource-router/task_bundle_remote`, `scnetresource-router/sif_register`, `scnetresource-router/sif_resolve`, `scnetresource-router/sif_verify`, `scnetresource-router/workspace_run`, `scnetresource-router/interactive_start`, `scnetresource-router/interactive_stop`, or any other `scnetresource-router/*` lifecycle tool directly.

## Why Scnet HPC Coordinator Instead of Direct Calls

| 风险 | 直接调用 | Scnet HPC Coordinator |
|------|---------|----------------------|
| 集群路由配置变更（tag 从 cpu→rocm） | ❌ 各 agent `choose_best` 各自失效，无统一报错 | ✅ Coordinator 集中检测，统一返回集群拒绝原因 |
| 资源余量不一致 | ❌ 各 agent 可能漏乘或错乘安全系数 | ✅ Coordinator 强制 2.5× wall time、≥2 nodes、1.5× memory |
| 取消作业入口缺失 | ❌ 工具被禁用时无替代路径 | ✅ Coordinator 报告详细错误 + 建议手动 scancel |
| 时间限制冲突 | ❌ agent 不知道 xian 集群 12h 限制 | ✅ Coordinator 在路由阶段检测并报告 |
| 错误处理发散 | ❌ 各 agent 各自解释 submit 失败原因 | ✅ Coordinator 统一结构化错误（error_type + suggestions） |
| dry_run/confirm 协议不一致 | ❌ 有的 agent 跳 dry_run 直接 confirm | ✅ Coordinator 强制 dry_run→confirm 顺序 |

## Agent Integration

1. Ensure `Scnet HPC Coordinator` is in your agent's `agents:` list.
2. When an HPC job lifecycle operation is needed, delegate to Scnet HPC Coordinator via `opencode task`.
3. In your delegation prompt, specify (see Information Flow Contract below for full schema):
   - `operation`: submit | cancel | download | monitor | status | probe
   - `command` (for submit): the command array to run
   - `estimated_wall_time_minutes` (for submit): **REQUIRED** — raw estimate before safety margins. The Coordinator MUST pass this as `requirements.time_minutes` to `task_run_auto`. If the upstream agent does not provide a wall-time estimate, the Coordinator MUST NOT silently submit — ask the upstream agent for an estimate or refuse with `error_type: MISSING_WALL_TIME`.
   - `requirements_hint`: backend, min_cpu_cores, preferred_partitions
   - `confirm`: true | false
4. Scnet HPC Coordinator returns structured results with `task_id`, `cluster`, `applied_margins`, `warnings`, and `monitoring_hint`.

## Operation Mapping

### Must Delegate to Scnet HPC Coordinator (🔄 Coordinator)

These are **job lifecycle operations** — centralized through Coordinator:

| You want to... | Delegate to Coordinator | NOT this |
|----------------|------------------------|----------|
| Submit a job | `opencode task("Scnet HPC Coordinator")` with `operation=submit` | `task_run_auto` directly |
| Submit with custom sbatch script | `opencode task("Scnet HPC Coordinator")` with `operation=submit` | `task_create_submit_auto` directly |
| Submit parameter sweep (array) | `opencode task("Scnet HPC Coordinator")` with `operation=submit` | `task_run_array_auto` directly |
| Cancel a job | `opencode task("Scnet HPC Coordinator")` with `operation=cancel` | `cancel` directly |
| Download results | `opencode task("Scnet HPC Coordinator")` with `operation=download` | `task_download_outputs` directly |
| Select best cluster | `opencode task("Scnet HPC Coordinator")` with `operation=status` | `choose_best` directly |
| Upload input files | `opencode task("Scnet HPC Coordinator")` with `operation=upload` | `upload` directly |
| Probe container | `opencode task("Scnet HPC Coordinator")` with `operation=probe` | `container_probe` directly |
| Retry failed array | `opencode task("Scnet HPC Coordinator")` with `operation=submit` | `task_array_retry_failed` directly |
| Import external job | `opencode task("Scnet HPC Coordinator")` with `operation=monitor` | `task_import` directly |
| SIF image management | `opencode task("Scnet HPC Coordinator")` with `operation=probe` | `sif_register/sif_resolve/sif_verify` directly |
| Register software in catalog | `opencode task("Scnet HPC Coordinator")` with `operation=probe` | `software_register` directly |
| Run workspace command (sync+submit+download) | `opencode task("Scnet HPC Coordinator")` with `operation=submit` | `workspace_run` directly |
| Start interactive session (jupyter/shell) | `opencode task("Scnet HPC Coordinator")` with `operation=interactive` | `interactive_start` directly |
| Stop interactive session | `opencode task("Scnet HPC Coordinator")` with `operation=interactive` | `interactive_stop` directly |

### May Call Directly (✅ Direct)

These are **lightweight read/monitor operations** — keep for efficiency:

| You want to... | Use this MCP tool |
|----------------|-------------------|
| Check cluster status | `status` / `status_multi` |
| Check job status | `job_status` |
| Monitor job output (tail) | `job_tail` / `task_tail` |
| Poll task completion | `task_poll` (cheap, read-only — cached task metadata) |
| List tasks | `task_list` |
| List task events | `task_events_list` |
| Check task artifacts | `task_artifacts` |
| Check array status | `task_array_status` |
| Read remote file | `remote_cat` |
| List remote directory | `remote_ls` |
| Search remote logs | `remote_grep` |
| Read remote file head/tail | `remote_head` / `remote_tail` |
| Find remote files | `remote_find` |
| Check remote file metadata | `remote_stat` |
| Create remote directory | `remote_mkdir` |
| Delete remote file | `remote_rm` |
| List queue | `queue_list` |
| Check partition snapshots | `partition_snapshots` |
| List SIF images | `sif_list` |
| List/help/schema tools | `tool_list` / `tool_help` / `tool_schema` |
| Query audit log | `audit_query` |
| Show environment config | `env_list` / `env_show` / `info` |
| Refresh task metadata | `task_refresh` (registry write — forces SSH + sacct; prefer `task_poll` for simple status queries) |
| Query software catalog (which clusters have software X) | `software_list` |
| Resolve software deployment details on a cluster | `software_resolve` |
| Diagnose a failed task | `task_diagnose` |
| Check interactive session status | `interactive_status` |

## Software Discovery Protocol — 软件发现协议

When an agent needs to find or verify whether simulation software (MCNP6, OpenMC, FISPACT-II, natf, etc.) is available on HPC clusters:

1. **FIRST**: Call `software_list(software="mcnp6")` to check which clusters have it registered.
2. **THEN**: Call `software_resolve(cluster="<cluster>", software="mcnp6")` to get deployment details (runtime, image, binary, MPI launcher).
3. **SUBMIT**: Use `task_run_auto(software="mcnp6", ...)` — the `software` parameter auto-resolves the profile.

**NEVER** use `remote_find` / `remote_ls` / `remote_cat` to search for software binaries or container images on cluster filesystems. The software catalog is the single source of truth.

| Scenario | Correct action | Wrong action |
|----------|---------------|---------------|
| "哪些集群有 MCNP？" | `software_list(software="mcnp6")` | `remote_find` on each cluster |
| "昆山有 mcnp 吗？" | `software_resolve(cluster="kunshan", software="mcnp6")` | `remote_ls /opt/` on kunshan |
| 用户说"曙光上有编译好的 mcnp" | `software_list(software="mcnp6")` 确认是否已注册 → 若未注册则提议 `software_register` | 盲目 `remote_find -name 'mcnp*'` |
| `software_resolve` 返回 `not_configured` | **停止**，告知用户该集群无此软件 | fallback 到 `remote_find` 搜文件系统 |

## Information Flow Contract

### Upstream → Coordinator (delegation prompt minimum)

```
operation: submit | cancel | download | monitor | status | probe
task_id: <string, required for cancel/download/monitor>
job_id: <string, required for cancel>
code: openmc | mcnp6 | fispact-ii | natf | tricys | custom
command: [<shell command array>, required for submit]
input_paths: [<string>, paths to upload before submit]
estimated_wall_time_minutes: <int, REQUIRED for submit — RAW estimate (pre-margin). Coordinator passes this as requirements.time_minutes to task_run_auto.>
estimated_memory_gb: <float, recommended for submit>
requirements_hint: {backend: "cpu"|"gpu"|"cuda"|"rocm", min_cpu_cores: int, preferred_partitions: [string]}
confirm: true | false  # MUST be false for initial preview
clusters: [<string>, optional: restrict cluster scope]
profile: <string, optional: container profile name>
```

### Coordinator → Upstream (returned in final message)

On success:
```
status: ✅ SUBMITTED | ✅ CANCELLED | ✅ DOWNLOADED | ✅ COMPLETED
task_id: <string>
job_id: <string>
cluster: <string>
partition: <string>
applied_margins: {wall_time: {raw_min, padded_min, multiplier}, nodes: {requested, rule}, memory: {raw_gb, padded_gb, multiplier}}
warnings: [<string>]
monitoring_hint: <string, e.g. "Use task_tail(task_id='...') to monitor">
```

On failure:
```
status: ❌ FAILED
error_type: ROUTE_FAILED | SUBMIT_FAILED | CANCEL_FAILED | DOWNLOAD_FAILED | TIMEOUT | RESOURCE_INSUFFICIENT
error_message: <string>
cluster_rejections: [{cluster: string, reason: string}]
suggestions: [<string>]
```

## Upstream Agent Integration Checklist

When modifying an agent to delegate to Scnet HPC Coordinator:

- [ ] `agents:` list includes `"Scnet HPC Coordinator"`
- [ ] `tools:` list removes all lifecycle scnetresource-router tools (see Operation Mapping above)
- [ ] `tools:` list retains all read/monitor scnetresource-router tools (see "May Call Directly" above)
- [ ] Body no longer references removed lifecycle tools directly
- [ ] Body includes delegation guidance: when HPC submission is needed, construct prompt per Information Flow Contract
- [ ] For Simulation Builder: Stage G references Scnet HPC Coordinator instead of `task_run_auto`
- [ ] For Task Executor: Domain Dispatch Protocol routes HPC keywords to Scnet HPC Coordinator

## MCP Unavailable Fallback

If the `scnetresource-router` MCP server is unavailable or `Scnet HPC Coordinator` subagent fails to launch:

1. **Do NOT silently fall back** to direct `scnetresource-router/*` tool calls at the upstream agent level.
2. Report the error to the user: `Scnet HPC Coordinator is unavailable. HPC job lifecycle operations cannot be performed at this time.`
3. If the user explicitly requests manual HPC operations (raw SSH, manual sbatch), ask the user to confirm before proceeding.
4. For monitoring-only tasks (cluster status, job tail), read/monitor tools are still available for direct use.

## Coordinator Hallucination Detection

When Scnet HPC Coordinator returns a result, the upstream agent MUST validate it is not hallucinated. The Coordinator hallucinates when the `scnetresource-router` MCP server is not connected but the model generates plausible-looking output instead of failing cleanly.

### Detection Signals (require 2+ to trigger)

| # | Signal | How to verify |
|---|--------|---------------|
| 1 | File paths in result don't exist | `ls` / `find` locally, or `remote_ls` on cluster |
| 2 | Claimed task_id not found | Call `task_list` or `task_tail` directly (read tools) |
| 3 | All direct scnetresource-router read tools also fail | Call `status` — if it errors, MCP is disconnected |
| 4 | Result contains implausibly perfect metadata | Exact byte sizes, future timestamps, or SIF tags that don't match known inventory |

### Handling

- **2+ signals confirmed** → Discard result. Mark task as `🛑 BLOCKED: Coordinator hallucinated`. Report to user.
- **Signal 3 alone (all read tools fail)** → MCP server disconnected. Follow "MCP Unavailable Fallback" above.
- **`TOOLS_UNAVAILABLE` in Coordinator response** → Not hallucination; Coordinator correctly detected disconnection. Follow fallback.

## Anti-Hallucination Protocol (Reusable Template)

> **Precedence**: This protocol is the operational implementation of the
> [Coordinator Hallucination Detection](#coordinator-hallucination-detection)
> signals table above. In case of conflict, this protocol takes precedence
> — it defines the mandatory verification workflow, while the Detection
> Signals table serves as a quick-reference symptom index.

This protocol applies whenever an upstream agent (Task Executor, Fusion
Deep Research, Simulation Builder, Simulation Analyst) delegates to the
Scnet HPC Coordinator and receives a response that includes claimed
`task_id` values, `job_id` values, or causal debugging narratives.

### For Upstream Callers

After receiving a Coordinator response, execute this independent
verification checklist. Each rule verifies the Coordinator's output
against an independent source of truth — never against the Coordinator's
own claims.

1. **Check MCP connectivity first.**
   Call `status` (no delegation — call the scnetresource-router tool
   directly). If `status` returns an error or `ok: false`, the MCP server
   is unreachable. Coordinator response is untrusted. Stop here and report
   `🛑 BLOCKED: MCP server unreachable`.

2. **Verify every claimed task_id.**
   For each `task_id` in the Coordinator response, call `task_list`
   directly (read tool, no delegation). If the task_id does not appear in
   the registry, it was fabricated. This is signal #2 from the Detection
   Signals table.

3. **Verify claimed file paths.**
   For each file path in the Coordinator response (SIF images, input
   files, output paths), use `ls` locally or `remote_ls` on the cluster
   to confirm existence. Missing paths are signal #1.

4. **Cross-reference tool-call counts against journald.**
   When the Coordinator report attributes failures to specific tool calls
   (e.g., "task_create_submit injected wrong project_code"), verify those
   tools were actually invoked:
   ```bash
   journalctl --user -u scnet-mcp-http.service --since "3 hours ago" -o cat \
     | grep -oE '"tool": "[^"]+"' | sort | uniq -c | sort -rn
   ```
   A count of 0 for the claimed tool confirms fabrication. This is the
   definitive forensic check.

5. **Apply the high-cardinality split rule.**
   When the Coordinator response contains **multiple** claimed task_ids
   (e.g., a batch submission report), verify them in **separate batches**
   rather than in a single sequence:
   - Split task_ids into groups of ≤ 5.
   - Verify one batch, pause, then verify the next.
   - If any batch fails verification, treat the **entire** response as
     untrusted (partial fabrication poisons the whole).
   - Rationale: hallucinated task_ids are often clustered; batch
     verification prevents a mixed genuine/fabricated response from
     slipping through.

**Decision matrix**:

| Signals confirmed | Action |
|-------------------|--------|
| Coordinator returns `TOOLS_UNAVAILABLE` | Not hallucination — Coordinator detected MCP disconnection. Follow "MCP Unavailable Fallback" above. No further signal checking needed. |
| 0 signals | Trust result. Proceed with downstream work. |
| 1 signal (ambiguous) | Re-delegate once with simplified prompt. If second response also triggers ≥1 signal, treat as hallucinated. |
| 2+ signals | Discard result. Mark task `🛑 BLOCKED: Coordinator hallucinated`. Report to user with evidence. |
| Signal #3 alone (all read tools fail) | MCP disconnected. Follow "MCP Unavailable Fallback" above. |

### For the Coordinator Itself

When the Coordinator is invoked with an HPC lifecycle operation, it
should self-validate before returning a result:

1. **Pre-flight connectivity check.**
   Before executing any write tool, call `status` or `tool_list` to
   confirm the MCP server is reachable. If not, return
   `TOOLS_UNAVAILABLE` immediately — do not generate a narrative report.

2. **Do not invent causal narratives.**
   When a tool call fails, report the raw error message and exit code.
   Do not generate speculative debugging analysis (e.g., "the error is
   caused by...", "this suggests that..."). If the error is ambiguous,
   say "error is ambiguous; use `task_diagnose` for structured
   diagnosis."

3. **Do not fabricate task_ids or job_ids.**
   Never include a task_id or job_id in the response unless it was
   returned by a scnetresource-router tool call. All task_ids must be
   verifiable via `task_list`.

4. **Include verifiability markers.**
   For every claimed task_id, include the tool name and timestamp of the
   call that produced it (e.g., "task_id `abc123` returned by
   `task_create_submit` at 2026-06-10T08:01:41Z"). This enables upstream
   callers to cross-reference against journald.

5. **High-cardinality transparency.**
   When returning > 5 task_ids (e.g., from a batch submission), prefix
   the list with the batch verification protocol note:
   `<!-- Batch: verify in groups of ≤5. See Anti-Hallucination Protocol. -->`
