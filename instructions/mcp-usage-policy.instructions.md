---
description: "MCP tool usage policy: use MCP APIs, verify tool-call results, parse environment variables safely, and never modify MCP server internals"
applyTo: "**"
revision: 2
---

# MCP Tool Usage Policy

When MCP server tools are available for a task, you **MUST** use them through their MCP interface. Do NOT directly read, modify, or operate on the underlying source code, configuration files, or data stores that an MCP server manages.

If an MCP server's functionality is insufficient or inconvenient:

1. **Report the limitation** to the user — describe what the MCP server should improve or add
2. **Do NOT** work around it by modifying the MCP server's source code or underlying systems
3. This applies even to the user's own MCP servers — never edit source code in other workspaces to "fix" or "enhance" an MCP tool

**Rationale**: MCP servers provide stable, tested interfaces. Bypassing them by directly manipulating their internals creates inconsistencies, breaks abstractions, and can corrupt state.

## Tool-Call Result Verification

Apply this rule to MCP tool calls and subagent delegations before using their output as evidence, state, task IDs, file paths, or user-visible conclusions. This fleet-wide rule supersedes duplicated per-agent wording when there is a conflict.

### Failure Signals

Treat any of the following as a failed or untrusted call result:

- **Fake tool-call JSON**: The response contains a fenced JSON block with a `"tool"` key instead of actual tool output.
- **Narrative fabrication**: The response claims task IDs, job IDs, file paths, or tool invocations that cannot be verified by available read/status tools or logs.
- **Empty or truncated output**: The response is blank, ends mid-sentence, or lacks the expected status/result fields.
- **Unavailable or timed out**: The server, subagent, or transport reports timeout, disconnected, disabled, or unavailable.
- **Structured failure**: The tool returns `ok: false`, `error`, `degraded: true`, or an equivalent failure/degradation marker.

### Retry and Fallback Policy

1. **Retry at most once** with a smaller, simpler prompt or argument set.
2. **Retry only failed items** in a batch; do not repeat successful calls.
3. **Do not blindly retry writes**. Repeat create/update/delete/submit operations only when the tool documents idempotency or when a read-back proves no side effect occurred.
4. **Use the documented fallback path** for the tool or agent. If none exists, mark the step degraded and state what was skipped.
5. **Stop after two consecutive failures** in the same stage and ask the user how to proceed, unless the agent-specific policy defines a safer non-blocking fallback.
6. **Never fabricate replacement results**. Unknown IDs, missing paths, and unavailable tools must be reported as unknown or unavailable.

### Semantic Scholar Required-Source Override

When a task explicitly requires public academic discovery, Semantic Scholar
metadata lookup, citation graph traversal, author publication lists, related-paper
recommendations, or Semantic Scholar verification, treat the `semantic-scholar`
MCP server as a required source. The generic fallback policy above does not allow
silent replacement of a failed required Semantic Scholar step with Dify, Zotero,
Crossref, arXiv, OpenAlex, crawl4ai, web search, or model memory.

Use this sequence instead:
1. Retry once with a smaller request (`limit`, `fields`, fewer IDs, or narrower
  query) while preserving successful batch items.
2. If rate-limited, wait/back off rather than skipping. Respect `Retry-After` when
  present; otherwise use sequential calls at about 1 request per second and
  increase delay for repeated `429` responses.
3. If the MCP server or transport is unavailable, diagnose the configured
  StreamableHTTP endpoint, container/service status, and MCP client config when
  available.
4. If still unresolved, return `FAILED` or `BLOCKED` for the affected public
  academic step with the exact tool, request shape, and failure reason.

Other sources may still supplement successful Semantic Scholar results, verify
DOI/publisher metadata, search the user's local library, or cover private KB
content. If Semantic Scholar successfully returns no relevant results after query
refinement and pagination, label any supplementary-source-only result explicitly
as non-Semantic-Scholar coverage rather than a fallback.

### Fallback Result Taxonomy

All fallback steps MUST use exactly one of the following outcome tags.
Gate instructions that consume these tags MUST NOT treat a skipped gate as
equivalent to a passed gate.

| Tag | Meaning | When to Use |
|-----|---------|-------------|
| **PASS** | Step completed fully, result is correct. | All assertions valid; no degradation. |
| **DEGRADED** | Step completed with fidelity loss. | Artifact usable but known quality gap (e.g., fallback font, reduced resolution). |
| **SKIPPED** | Step intentionally skipped — dependency unavailable. | MCP server down, optional tool not present, non-blocking prerequisite missing. |
| **FAILED** | Step attempted and failed. | Tool returned error, assertion violated, timeout. Blocking if the step was mandatory. |
| **BLOCKED** | Step could not start — prerequisite unmet. | User clarification needed, upstream chain broken, missing required config key. |

Rules for gate authors:

- A `SKIPPED` gate MUST NOT be counted as `PASS`.  Deliverables that skipped a
  mandatory gate must carry the `SKIPPED` marker and a user-visible warning.
- A `DEGRADED` outcome MUST record the degradation reason (e.g. "image resized
  to fit preview budget") so the operator can decide whether to ship.
- After two consecutive `FAILED` retries or any `BLOCKED` that requires user
  action, stop the workflow and ask the user how to proceed.

## Environment Parsing and Secret Hygiene

When a tool, server, or model provider depends on environment variables, parse configuration conservatively:

- **Distinguish states**: `unset`, empty string, placeholder value, malformed value, and valid-looking value are different states.
- **Treat placeholders as missing**: Values such as `TODO`, `TBD`, `changeme`, `your_api_key`, `xxx`, `<...>`, or `${...}` are not usable credentials.
- **Never print secrets**: Report only variable names and coarse status such as `set`, `unset`, `empty`, or `placeholder`. Do not echo tokens, API keys, passwords, cookies, or private URLs with embedded credentials.
- **Do not ask for secrets in chat**: Tell the user to enter secrets directly into the terminal, environment file, or provider UI.
- **Do not invent defaults for required config**: If a required key or base URL is absent, stop that integration path and report the missing variable.
- **Validate non-secret fields**: Check URLs for scheme/host, ports for integer range, booleans against an explicit allow-list, and model names against the provider/tool documentation when available.
- **Record provenance without values**: If configuration affects a result, state the source (`env`, config file, tool response) without exposing sensitive content.
