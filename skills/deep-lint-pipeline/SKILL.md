---
name: "deep-lint-pipeline"
description: "Full-chain lint pipeline: citation-lint/pipeline_scan → manuscript-lint/full_scan → formatforge/lint_markdown → de-ai-fier/vale_gate_file. Use when a document with bibliography needs comprehensive pre-submission quality checks. 全链路文稿质量检查流水线, 参考文献+正文+格式+术语一站式检查."
revision: 1
---

# Deep Lint Pipeline — 全链路文稿质量检查

> Crystallized from: P4 deep integration plan (citation-lint + manuscript-lint + formatforge + de-ai-fier).
> Trigger: T2 (≥2 occurrences of multi-tool lint workflows)

## When to Use

- Manuscript with a .bib file needs comprehensive pre-submission quality checks.
- User asks for "全链路检查", "deep lint", "pipeline scan", or "全面质量检查".
- Format Engineer or Academic Writer needs to validate both bibliography and prose before format export.
- Paper Reviewer needs a pre-review quality baseline.

## When NOT to Use

- No .bib file present (use manuscript-lint + formatforge directly).
- Single-tool check only (use the individual tool directly).
- Text-only document without bibliography (use manuscript-lint + de-ai-fier directly).

## Workflow

### Step 1: citation-lint/pipeline_scan

```
citation-lint/pipeline_scan(path="refs.bib", manuscript_path="manuscript.md", profile="<journal>", min_level="info")
```

- Runs all citation-lint rules (BibTeX, DOI, consistency, crossref, journal, arXiv, publisher, author).
- Returns `next_steps` list with instructions for downstream tools.
- If `manuscript_path` is provided, also validates cross-references between .bib and manuscript.

### Step 2: manuscript-lint/full_scan

```
manuscript-lint/full_scan(path="manuscript.md")
```

- Checks manuscript structure, numbering, citations, acronyms, figures, tables, formatting.
- Returns structured findings with severity levels.

### Step 3: formatforge/lint_markdown

```
formatforge/lint_markdown(path="manuscript.md")
```

- Validates markdown for scientific writing conventions.
- Optionally run `formatforge/autofix_markdown` for auto-fixable issues.

### Step 4: de-ai-fier/vale_gate_file

```
de-ai-fier/vale_gate_file(path="manuscript.md")
```

- Checks terminology consistency, unit conventions, and AI-tone patterns.
- Blocks delivery if blocking issues found (severity ≥ Warning).

### Fallback Strategy

| Failure | Fallback |
|---------|----------|
| citation-lint unavailable | Skip bibliography check, note in report |
| manuscript-lint unavailable | Skip structure/format check, note in report |
| formatforge unavailable | Skip markdown lint, note in report |
| de-ai-fier unavailable | Follow `instructions/de-ai-fier-gate.instructions.md` MCP→HTTP→SKIPPED ladder; skip only if both unavailable |
| citation-lint finds crossref issues | Continue pipeline; note unresolved citations |

## Report Aggregation

Aggregate findings across all tools into a single summary:

```
## Deep Lint Pipeline Report

| Stage | Tool | Status | Findings (W/E/I) | Notes |
|-------|------|--------|-------------------|-------|
| 1 | citation-lint/pipeline_scan | ✅ | 3/0/5 | DOI format issues in 2 entries |
| 2 | manuscript-lint/full_scan | ✅ | 1/2/8 | Missing figure reference |
| 3 | formatforge/lint_markdown | ✅ | 0/0/2 | Minor formatting |
| 4 | de-ai-fier/vale_gate_file | ✅ | 0/1/3 | AI-tone in introduction |
```

## Common Pitfalls

1. **Skipping citation-lint when .bib exists**: Always run bibliography checks first; fixing .bib issues after prose edits wastes effort.
2. **Not passing manuscript_path to pipeline_scan**: Cross-reference validation (BibTeX keys → manuscript citations) is skipped without it.
3. **Ignoring next_steps**: `citation-lint/pipeline_scan` returns a `next_steps` list with pre-configured downstream tool calls — use them directly.
4. **Wrong order**: Always run citation-lint BEFORE manuscript-lint (bib errors may cause citation-integrity false positives in manuscript-lint).

## Revision Log

| Revision | Date | Changes |
|----------|------|---------|
| 1 | 2026-05-12 | Initial crystallization from P4 plan |
