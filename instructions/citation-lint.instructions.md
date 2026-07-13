---
description: "citation-lint MCP tool integration: deterministic BibTeX validation for DOI format, journal names, cross-entry consistency, bib↔manuscript key matching. Use on .bib files before or alongside manuscript-lint. 参考文献 lint, BibTeX 校验, DOI 格式, 期刊缩写, 交叉引用, 自动修复建议."
applyTo: "paper-reviewer,academic-writer,citation-scanner,review-responder,proposal-writer"
revision: 3
---

# citation-lint MCP Integration

## What it is

citation-lint is a deterministic, rule-based MCP server for BibTeX bibliography validation. No LLM involved, runs in < 1 second, reproducible results. Checks DOI format, journal name consistency, entry syntax, cross-entry duplicates, and bib↔manuscript citation key matching.

## When to call

| Context | Timing | Tools |
|---------|--------|-------|
| **Review agents** (paper-reviewer) | After intake, if `.bib` file available | `full_scan` on the `.bib` |
| **Writing agents** (academic-writer, proposal-writer) | At quality gate, before delivery | `full_scan` with venue profile |
| **Citation scanner** | As primary analysis tool | `full_scan` + individual audits |
| **Review responder** | Before delivery | `full_scan` to verify bib fixes |
| **Deep lint pipeline** | Full-chain quality check (bib + manuscript + format + terminology) | `pipeline_scan` on `.bib` with `manuscript_path` |

## Tool quick reference

### `full_scan` — one-call aggregate

```jsonc
full_scan(path="/abs/path/refs.bib", profile="default", manuscript="/abs/path/paper.tex", min_level="warning")
// profile: default | strict
// manuscript: optional path for bib↔manuscript key matching
// min_level: info | warning | error
```

Runs all audit tools: `bibtex_audit`, `doi_audit`, `consistency_audit`, `journal_audit`, `crossref_audit`, plus PF-001 DOI check.

### `pipeline_scan` — deep lint pipeline entry point

```jsonc
pipeline_scan(path="/abs/path/refs.bib", manuscript_path="/abs/path/manuscript.md", profile="nf", min_level="info")
// profile: nf | fst | pst | fed | default | strict
// manuscript_path: optional, enables bib↔manuscript cross-ref validation
// min_level: info | warning | error
```

Same as `full_scan` but also returns `next_steps` — a list of downstream tool calls
(`manuscript-lint/full_scan`, `formatforge/lint_markdown`, `de-ai-fier/vale_gate_file`)
with pre-configured parameters. Use this as the first step in the deep-lint-pipeline.

### Individual tools (call when only one dimension needed)

| Tool | Scope |
|------|-------|
| `bibtex_audit` | BX-001 missing required fields, BX-002 empty fields, BX-003 @preamble issues, BX-004 suspicious entry types, BX-005 field naming, BX-006 unrecommended fields |
| `doi_audit` | DO-001 invalid DOI format, DO-002 URL in DOI field, DO-003 DOI in wrong field, DO-004 DOI prefix consistency |
| `consistency_audit` | CN-001 duplicate keys, CN-002 near-duplicate entries, CN-003 author format inconsistency, CN-004 year anomalies, CN-005 ISBN/ISSN validation, CN-006 URL format |
| `journal_audit` | JN-001 journal name style (abbreviated/full/any), JN-002 possible journal name typo |
| `crossref_audit` | CR-001 undefined citations, CR-002 unused bib keys, CR-003 key case mismatch |
| `multi_bib_audit` | CR-004 duplicate keys across multiple `.bib` files |
| `ris_scan` | Parse RIS (.ris) file and run all audits (bibtex, doi, arxiv, consistency, publisher, author, journal) |
| `pipeline_scan` | Deep-lint pipeline entry point — runs full_scan + returns next_steps for downstream tools |

## Consuming findings

Each finding has: `rule` (e.g. `DO-002`), `level` (error/warning/info), `line`, `message`, `snippet`, `suggestion`, stable `fid`.

- **error** findings = blocking (must resolve before delivery)
- **warning** findings = should review (may accept with justification)
- **info** findings = advisory

### Auto-fix data (v0.5.0+)

Some findings include a `fix` object with actionable repair metadata:

```jsonc
{
  "field": "doi",          // BibTeX field to modify
  "entry_key": "smith2024", // entry key
  "action": "replace",     // "replace" existing value or "add" new field
  "old_value": "https://doi.org/10.1088/...",
  "new_value": "10.1088/..."
}
```

Rules with fix data: DO-002 (replace URL→bare DOI), DO-003 (add doi field), JN-001 abbreviated/full mode (replace journal name), JN-002 (replace typo journal name). When `fix` is present, suggest the specific correction to the user rather than generic advice.

## Relationship to other lint tools

| Tool | Layer | Scope |
|------|-------|-------|
| `formatforge/lint_markdown` | Container format | Markdown syntax correctness |
| `de-ai-fier/vale_gate_file` | Style/terminology | AI-tone, term consistency, unit symbols |
| `manuscript-lint/full_scan` | Content structure | Section presence, fig/table numbering, citation integrity, provenance, acronyms |
| **`citation-lint/full_scan`** | **Bibliography** | **BibTeX syntax, DOI format, journal names, cross-entry consistency, bib↔manuscript key matching** |

Call order when both manuscript and `.bib` are available: `citation-lint/pipeline_scan` (on `.bib`) → `manuscript-lint/full_scan` (on manuscript) → `formatforge/lint_markdown` → `de-ai-fier/vale_gate_file`. For simpler cases without downstream lint, `full_scan` still works. See `skills/deep-lint-pipeline/SKILL.md` for the full workflow.

## Version

Compatible with citation-lint v0.8.0+
