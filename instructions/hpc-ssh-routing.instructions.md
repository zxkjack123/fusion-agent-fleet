---
description: "HPC SSH routing policy: use scnetresource-router MCP tools instead of raw SSH/scp/rsync for all HPC cluster interactions. 禁止直接SSH到曙光/算网集群, 必须通过 scnetresource-router MCP 工具. Applies to: remote job submission, file transfer, log inspection, queue status, remote file operations on SLURM clusters."
applyTo: "fusion-deep-research,scnet-hpc-coordinator,simulation-analyst,simulation-builder,task-executor"
revision: 3
---

# HPC SSH Routing Policy

## Core Rule

When interacting with HPC/SLURM clusters (Sugon, Shandong, Sichuan, Xi'an, Kunshan, Harbin, Xiongheng, or any cluster configured in scnetresource-router), you **MUST** use `scnetresource-router` MCP tools. Do NOT:

- Run `ssh user@host` commands in the terminal
- Run `scp`, `rsync`, or `sftp` commands directly
- Write scripts that shell out to `ssh`/`scp`
- Use `paramiko`, `fabric`, or `subprocess` to SSH in user code

## Why

The scnetresource-router MCP server provides:
- **Connection pooling** with keepalive — avoids repeated SSH handshakes that trigger cluster security alerts
- **Task tracking** — every job is registered with task_id for monitoring and artifact retrieval
- **Path safety** — prevents accidental writes outside designated work directories
- **Confirmation protocol** — destructive operations require explicit `confirm=true`
- **Structured error handling** — consistent `error_type` / `hint` / `schema_hint` for agent self-correction

Direct SSH bypasses all of these protections.

## Operation Mapping

| You want to... | Use this MCP tool | NOT this |
|----------------|-------------------|----------|
| Check cluster status | `status` / `status_multi` | `ssh host squeue` |
| Submit a job | `task_run_auto` / `task_create_submit_auto` | `ssh host sbatch` |
| Check job status | `task_tail` / `task_poll` / `job_status` | `ssh host squeue -j` |
| Read remote file | `remote_cat` / `remote_head` / `remote_tail` | `ssh host cat` |
| List remote directory | `remote_ls` / `remote_find` | `ssh host ls` |
| Search remote logs | `remote_grep` | `ssh host grep` |
| Upload file | `upload` / `task_upload_inputs` | `scp local host:remote` |
| Download results | `download` / `task_download_outputs` | `scp host:remote local` |
| Create remote directory | `remote_mkdir` | `ssh host mkdir` |
| Delete remote file | `remote_rm` | `ssh host rm` |
| Check file metadata | `remote_stat` | `ssh host stat` |
| Cancel a job | `cancel` | `ssh host scancel` |
| Run workspace command | `workspace_run` | `ssh host 'cd ~/project && python train.py'` |
| Start interactive session | `interactive_start` | `ssh -L 8888:node:8888 host` |
| Stop interactive session | `interactive_stop` | `ssh host scancel <jobid>` |
| Diagnose failed task | `task_diagnose` | `ssh host 'cat slurm-*.err'` |

## Coordinator Delegation Rule

For HPC **lifecycle operations** (submit, cancel, download, upload, cluster selection, container probe, SIF image registration, workspace run, interactive start/stop), agents **MUST delegate to the Scnet HPC Coordinator** subagent rather than calling scnetresource-router tools directly. This is an **additional layer** on top of the Core Rule above — the Core Rule still applies (no raw SSH), but lifecycle tools are now routed through the Coordinator.

| Operation Type | How to Access | Rationale |
|----------------|---------------|-----------|
| Lifecycle: submit, cancel, download, upload, choose_best, task_run_auto, task_download_outputs, task_array_download, container_probe, sif_register, workspace_run, interactive_start, interactive_stop, etc. | **Delegate to Scnet HPC Coordinator** via `opencode task` | Centralized margin enforcement, task tracking, error handling |
| Read/monitor: status, job_tail, task_tail, remote_ls, remote_cat, remote_grep, task_list, task_array_status, task_diagnose, interactive_status, etc. | **Direct scnetresource-router tool calls** (as in Operation Mapping above) | Low latency, no lifecycle side effects |

Full delegation protocol and information flow contract: see `instructions/scnet-hpc-coordinator.instructions.md`.

### Self-Exclusion

This delegation rule does **NOT** apply to the **Scnet HPC Coordinator** agent itself — it is the sole agent authorized to call lifecycle scnetresource-router tools directly.

## When MCP Tools Are Unavailable — MCP 不可用降级

If `scnetresource-router` tools are not loaded or the MCP server is down:

1. **Do NOT propose agent-executed direct SSH, scp, rsync, or any raw-terminal
   fallback.** The agent itself has no safe way to operate SSH without bypassing
   the protections described above (connection pooling, path safety, confirmation
   protocol, structured error handling).
2. **Mark the HPC step as BLOCKED.** Use the `BLOCKED` outcome tag per
   `instructions/mcp-usage-policy.instructions.md` Fallback Result Taxonomy.
3. **Tell the user to operate SSH manually outside the agent.** Provide the
   exact commands the user should run (e.g., `ssh user@host sbatch ...`,
   `scp local user@host:path`), but do not execute them.
4. **Do NOT ask whether the agent should fall back to direct SSH, scp, or
   rsync.** The answer is always no — agent-executed raw SSH is never a
   permitted fallback.

## Discovery

Use `tool_list()` for the full tool catalog. Use `tool_help(tool_name=X)` for detailed usage of any tool. Refer to `AGENTS.md` in the scnet_resource workspace for common workflow patterns.
