---
description: "manuscript-lint MCP tool integration: deterministic content-layer lint for scientific manuscripts. Use as pre-filter before LLM review/writing to catch structural, numbering, citation, and consistency issues cheaply. 稿件内容 lint, 图表编号, 引用完整性, 章节检查, 数值一致性, 缩写检查."
applyTo: "paper-reviewer,innovation-reviewer,methodology-deep-reviewer,academic-writer,proposal-writer,patent-writer,review-responder,structure-format-scanner"
revision: 1
---

# manuscript-lint MCP Integration

## What it is

manuscript-lint is a deterministic, rule-based MCP server for scientific manuscript content-layer checks. No LLM involved, runs in < 1 second, reproducible results.

## When to call

| Context | Timing | Tools |
|---------|--------|-------|
| **Review agents** (paper-reviewer, innovation-reviewer) | After intake, before LLM analysis | `full_scan` on the manuscript |
| **Writing agents** (academic-writer, proposal-writer, patent-writer) | At quality gate, before delivery | `full_scan` + relevant Tier 2 |
| **Specialist sub-agents** (structure-format-scanner, methodology-deep-reviewer) | As primary analysis tools | Specific tools per dimension |
| **Review responder** | Before delivery | `full_scan` + `response_coverage` |

## Tool quick reference

### `full_scan` — one-call Tier 1 aggregate

```jsonc
full_scan(path="/abs/path/manuscript.md", profile="paper", min_level="warning")
// profile: paper | patent | report | thesis | proposal
// min_level: info | warning | error
```

Runs all Tier 1 tools: `fig_table_audit`, `section_presence`, `citation_integrity`, `ref_statistics`, `acronym_audit`, `provenance_coverage`, `formatting_audit`.

### Tier 2 tools (call individually)

| Tool | Use when |
|------|----------|
| `numeric_consistency` | Cross-checking values across Abstract/Results/Tables |
| `plausibility_check` | Validating physical quantities against known ranges |
| `contradiction_scan` | Detecting "X uses A" vs "X uses B" contradictions |
| `abstract_conclusion_align` | Comparing Abstract claims with Conclusions |
| `claim_tree_validate` | Patent claim numbering and dependency chain |
| `response_coverage` | Review response letter completeness |
| `method_result_orphan` | Methods↔Results cross-reference |
| `title_abstract_check` | Title length, abstract word count |
| `crossref_audit` | Supplementary/section/appendix cross-refs + DOI format |

## Consuming findings

Each finding has: `rule` (e.g. `FT-003`), `level` (error/warning/info), `line`, `message`, `snippet`, `suggestion`, stable `fid`.

- **error** findings = blocking (must resolve before delivery)
- **warning** findings = should review (may accept with justification)
- **info** findings = advisory

## Relationship to other lint tools

| Tool | Layer | Scope |
|------|-------|-------|
| `formatforge/lint_markdown` | Container format | Markdown syntax correctness |
| `de-ai-fier/vale_gate_file` | Style/terminology | AI-tone, term consistency, unit symbols |
| **`manuscript-lint/full_scan`** | **Content structure** | **Section presence, fig/table numbering, citation integrity, provenance, acronyms** |

These three are complementary. Call order: `manuscript-lint` → `formatforge` → `de-ai-fier`.
