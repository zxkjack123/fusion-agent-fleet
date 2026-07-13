---
description: "Session memory policy: use session-memory MCP server to recall relevant experience from past OpenCode conversations before starting unfamiliar tasks, and to search for specific error messages or configurations encountered previously. 历史对话记忆策略, 经验召回, 报错搜索, 避免重复踩坑."
applyTo: "**"
revision: 1
---

# Session Memory MCP Policy — 历史对话记忆策略

The `session-memory` MCP server indexes past OpenCode conversations and provides three tools for retrieving historical experience. Use them to avoid repeating past mistakes and to leverage previously discovered solutions.

## Scope

This policy applies whenever you need to:

- **Recall past experience** before starting a task in a domain where the user has prior debugging/configuration history
- **Search for specific errors** encountered in previous conversations (error messages, command outputs, configuration values)
- **Refresh the search index** when searches return unexpectedly empty results

## Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `memory_recall(task_description=...)` | Natural language task → related conversation fragments (with ±2 messages context) | Task startup: collect relevant past experience |
| `memory_search(query=...)` | Keyword exact search (all words must match) | Mid-task: look up specific error messages, commands, config items |
| `memory_ingest()` | Refresh/rebuild the search index (default: incremental; `full=True`: full rebuild) | When `memory_search` returns empty unexpectedly |

Optional filters for `memory_search`: `workspace` (substring match), `role` (user/assistant), `time_from`/`time_to` (ISO 8601).

## Rules

1. **R1 — Startup recall**: When beginning a task in a domain likely to have prior history (HPC job submission, container debugging, simulation setup, MCP configuration, etc.), call `memory_recall(task_description=<concise task summary>)` to collect relevant experience. This is a judgment call — skip if the task is clearly novel or trivial.
2. **R2 — Error search**: When encountering a specific error message or needing a previously used command/configuration, call `memory_search(query=<key terms>)` for precise lookup.
3. **R3 — Empty result recovery**: If `memory_search` returns empty results, call `memory_ingest()` once to refresh the index, then retry the search. Do not call `memory_ingest` repeatedly.
4. **R4 — Reference only**: Recall results are **reference material**, not authoritative. Always verify against the current codebase via `read`/`search` tools. Current code state takes precedence over historical conversation snippets.
5. **R5 — Minimal Viable Information (MVI)**: Do not call `memory_recall` inside loops or iterative steps. Call it once at task startup, and optionally call `memory_search` when a specific lookup need arises. Do not bulk-inject historical conversation into context.

## MCP Unavailable Fallback

If the `session-memory` MCP server is unavailable (tools not loaded, connection timeout, server down):

1. **Do NOT block the workflow.** Skip the recall/search step.
2. Output a brief warning: `⚠️ session-memory MCP unavailable, skipping history recall.`
3. Proceed with normal task execution using available context (user memory, repo memory, code search).

## Relationship to Existing Memory Systems

| System | Storage | Scope | Use Case |
|--------|---------|-------|----------|
| OpenCode built-in `/memories/` | Persistent markdown files in workspace | User memory (cross-workspace), repo memory (per-repo), session memory (per-conversation) | Curated knowledge notes, manually persisted insights |
| `session-memory` MCP | Indexed database of past OpenCode logs | All past conversations, searchable | Automatic recall of debugging experience, error patterns, configuration discoveries |

These two systems are **complementary**:
- `/memories/` contains curated, distilled knowledge that the user explicitly chose to persist.
- `session-memory` MCP contains raw conversation history that may hold useful context not yet curated.
- When the `memory-nudge` instruction triggers knowledge persistence, check `session-memory` for duplicates to avoid re-persisting already-discussed knowledge (see `instructions/memory-nudge.instructions.md`).
