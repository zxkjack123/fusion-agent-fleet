---
description: "formatforge MCP tool inventory: 29 tools covering bidirectional conversion (markdown/docx/latex/epub/quarto), linting, validation, templates, references, and WPS quirks. Use formatforge instead of pandoc/raw shell for any document conversion. 文档转换, 格式工具, docx-markdown 双向转换, latex 转换, epub 转换, quarto, 模板, 引用检查, WPS 兼容."
applyTo: "**"
revision: 5
---

# formatforge MCP Tool Inventory

**Core rule**: For ANY document conversion task (markdown ⇄ docx ⇄ latex ⇄ epub, quarto rendering, WPS docx repair), call a `formatforge/*` tool first. Do NOT shell out to `pandoc`, `latex`, or write custom conversion scripts unless formatforge has been verified to lack the capability via `formatforge/doctor` or a failed call.

## Bidirectional Conversion (12 tools)

| From → To | Tool |
|-----------|------|
| markdown → docx | `convert_markdown_to_docx` |
| markdown → latex | `convert_markdown_to_latex` |
| markdown → epub | `convert_markdown_to_epub` |
| **docx → markdown** | **`convert_docx_to_markdown`** |
| docx → latex | `convert_docx_to_latex` |
| docx → epub | `convert_docx_to_epub` |
| latex → docx | `convert_latex_to_docx` |
| quarto sources → multi-format | `convert_quarto` |
| markdown → docx (publish pipeline with template + refs) | `publish_markdown_to_docx` |
| markdown → resource scan | `scen_markdown_resources` |
| docx normalization (in-place styling cleanup) | `docx_normalize` |
| backflow diff (compare two converted artifacts) | `backflow_diff` |

**Always prefer `convert_docx_to_markdown` over pandoc** for docx → markdown. It already handles grid-table cleanup, image extraction, and footnotes consistent with the rest of the formatforge pipeline.

## Linting & Validation (7 tools)

| Tool | Purpose |
|------|---------|
| `lint_markdown` | Scientific writing convention checks on markdown |
| `autofix_markdown` | Apply auto-fixable markdown lint issues |
| `validate_docx` | Schema/structure validation of a docx file |
| `validate_latex` | LaTeX source validation |
| `refs_check` | Verify cross-references resolve |
| `refs_lint` | Lint reference/citation formatting |
| `doctor` | Environment diagnostics (engines, fonts, templates available) |

## EPUB Quality Suite (3 tools)

| Tool | Purpose |
|------|---------|
| `epub_preflight` | Pre-conversion EPUB readiness check |
| `epub_qa` | Post-conversion EPUB quality audit |
| `epub_fix` | Apply automated EPUB repairs |

## WPS Compatibility (3 tools)

| Tool | Purpose |
|------|---------|
| `wps_scan` | Scan docx for WPS-specific quirks |
| `wps_detect` | Detect whether a docx originated from WPS |
| `wps_fix` | Repair WPS-specific docx issues for cross-tool compatibility |

## Templates & Configuration (4 tools)

| Tool | Purpose |
|------|---------|
| `template_list` | List available conversion templates |
| `template_install` | Install a new template |
| `template_validate` | Validate a template definition |
| `get_effective_config` | Show resolved configuration for current call context |

## Standard & Template Selection Guide

When converting markdown → docx, pass `standard=<key>` to auto-configure CSL, captions, reference doc, and template. **Always specify a standard** rather than relying on the default.

### Quick Selection Table

| User Scenario | Standard Key | Template | CSL | Lang |
|---------------|-------------|----------|-----|------|
| Chinese scientific/technical report (中英文混合科技报告) | `report-zh` | report_cn_gov | GB/T 7714-2015 numeric | zh-CN |
| Chinese gov-style report (政府/院所报告) | `report-cn-gov` | report_cn_gov | GB/T 7714-2015 numeric | zh-CN |
| NSFC proposal (国自然申请书) | `nsfc` | nsfc | GB/T 7714-2015 numeric | zh-CN |
| Chinese thesis (学位论文) | `gbt7714-2015-numeric` | thesis_zh_gbt | GB/T 7714-2015 numeric | zh-CN |
| Chinese patent (专利) | `patent-cn` | patent_cn | GB/T 7714-2015 numeric | zh-CN |
| English IEEE paper | `ieee` | report_en | IEEE | en-US |
| English APA paper | `apa7` | report_en | APA 7th | en-US |
| Fusion Engineering and Design | `fusion-engineering-design` | fusion_engineering_design | Elsevier w/ titles | en-US |
| Nuclear Fusion (IAEA) | `nuclear-fusion` | nuclear_fusion | IoP numeric | en-US |
| Nature / Science | `nature` / `science` | report_en | Nature / Science | en-US |
| Elsevier generic | `elsevier` | report_en | Elsevier w/ titles | en-US |
| Springer generic | `springer` | report_en | Springer author-date | en-US |
| English thesis / general report | `thesis-en` | report_en | APA | en-US |

### Template Styling Quick Reference

| Template | Body Font | Heading Font | English Font | Key Features |
|----------|-----------|-------------|--------------|--------------|
| `report_cn_gov` | 宋体 (SimSun) | 黑体 (SimHei) | Times New Roman | Fixed line spacing, zh-CN captions, three-line tables |
| `thesis_zh_gbt` | 宋体 (SimSun) | 宋体 (bold) | Times New Roman | Minimal heading styling, generic Chinese |
| `report_en` | Times New Roman | Times New Roman (bold) | Times New Roman | Standard English academic |
| `fusion_engineering_design` | Custom fusion | Custom fusion | Custom fusion | Elsevier 2-column aware |
| `nuclear_fusion` | Custom fusion | Custom fusion | Custom fusion | IoP style |
| `nsfc` | 宋体 | 黑体 | Times New Roman | NSFC page layout |
| `patent_cn` | 宋体 | 黑体 | Times New Roman | Patent format margins |

### Aliases (all resolve to the same standard)

- **report-zh**: `report_zh`, `report-chinese`, `zh-report`, `chinese-report`, `sci-report-zh`, `scientific-report-zh`, `report-zh-sci`, `chinese-scientific-report`
- **ieee**: `ieee-conference`, `ieee-journal`, `ieee_conference`
- **gbt7714-2015-numeric**: `gbt7714`, `gb-t-7714`, `gbt7714-numeric`

### Decision Logic for Agents

1. **Chinese content with bilingual (中英混合)?** → `report-zh` (SimSun + SimHei + TNR, GB/T 7714)
2. **Chinese thesis?** → `gbt7714-2015-numeric` (generic GB/T 7714 without opinionated heading fonts)
3. **English paper for specific journal?** → Use journal name as key (`ieee`, `nuclear-fusion`, etc.)
4. **English generic report/paper?** → `ieee` or `apa7`
5. **NSFC proposal?** → `nsfc`
6. **Unsure?** → Call `template_list` to see installed templates, then pick by venue

## EPUB Workflow Recipe

For any markdown/docx → EPUB deliverable, run the pipeline in this order. Skip steps only when the rationale is explicit.

1. **Preflight** — `epub_preflight` on the source (markdown or docx). Surfaces missing metadata (title/author/language/cover), structural gaps (no chapter headings), and unsupported assets (raw HTML, oversized images). If preflight returns `ok:false`, fix the source before converting.
2. **Convert** — `convert_markdown_to_epub` or `convert_docx_to_epub`. Always pass a `profile` when targeting a known store:
   - `profile="kdp"` → Amazon Kindle Direct Publishing (KF8-compatible CSS, embedded cover, single OPF spine).
   - `profile="ingramspark"` → IngramSpark distribution (strict EPUB 3.2, validated metadata, no inline JS).
   - omit `profile` for generic EPUB 3 output suitable for Calibre / Apple Books.
3. **QA** — `epub_qa` on the produced `.epub`. Returns `validation` (epubcheck issues), `accessibility` (alt-text, language tags, reading order), and `store_readiness` (per-profile gates). Treat any `severity: error` as blocking.
4. **Fix** — `epub_fix` on the produced `.epub` only when `epub_qa` reports auto-fixable issues (missing language tag, malformed nav, redundant whitespace). **Skip** `epub_fix` when:
   - `epub_qa.ok == true` (nothing to fix);
   - all reported issues are `severity: warning` and not store-blocking;
   - the issue is in source content (rewrite the markdown/docx and re-convert instead — `epub_fix` cannot regenerate semantic structure).

Re-run `epub_qa` after `epub_fix` to confirm closure.

## Common Pitfalls

- **Do NOT fall back to pandoc** without first attempting `convert_docx_to_markdown`. The agent prompt that triggered this instruction file existed because an agent assumed formatforge was markdown→X only.
- `publish_markdown_to_docx` is the high-level "lint + refs_check + convert + template" pipeline. Prefer it over chaining individual tools when producing a final deliverable.
- `docx_normalize` operates in-place on a docx — back up the file first if the original must be preserved.
- For docx files of unknown origin, run `wps_detect` before conversion; WPS-saved docx may need `wps_fix` first to avoid converter errors.
- `doctor` should be run when a converter call fails with environment-related errors (missing engine, missing font, missing template).

## Fallback Policy — NO PANDOC FALLBACK

**formatforge is the authoritative conversion engine.** The formatforge MCP server
runs as a StreamableHTTP service (`http://127.0.0.1:8003/mcp`) with
`restart: unless-stopped` and is expected to be always available.

### When a formatforge tool call fails

Follow this escalation ladder — **do not skip steps**:

1. **Retry once**. StreamableHTTP sessions can drop transiently. Retry the same
   tool call with identical arguments. If the retry succeeds, proceed normally
   and note `[formatforge: retry succeeded]` in output.
2. **Run `formatforge/doctor`**. If the retry also fails, call
   `formatforge/doctor` to check server health, available engines, fonts, and
   templates. The doctor output will indicate whether this is an environment
   issue (missing engine/font) or a server issue.
3. **Report to user — DO NOT silently switch tools.** If formatforge is
   confirmed unavailable or missing a required capability, report to the user
   with:
   - The failed tool name and arguments
   - The error details from the tool response or doctor output
   - A clear statement: `⚠️ formatforge unavailable — [reason]. Conversion blocked.`
   
   **Do NOT fall back to pandoc, LibreOffice, or shell tools as a substitute.**
   The user will decide whether to:
   - Restart the formatforge MCP server (`docker restart formatforge-mcp`)
   - Approve a one-time pandoc fallback for this specific conversion
   - Wait and retry later

### When pandoc/shell fallback IS acceptable (explicit user approval only)

The ONLY case where pandoc/shell fallback is acceptable is when:
- `formatforge/doctor` confirms the server is unreachable after a restart
  attempt, AND
- The user explicitly approves: "用 pandoc 吧" / "fall back to pandoc"

**Never** preemptively reach for pandoc just because a formatforge tool call
returned an error. Always escalate through the ladder above.

### Quick recovery command

If the formatforge MCP server needs restarting:
```bash
docker restart formatforge-mcp && sleep 3 && docker ps --filter name=formatforge-mcp --format '{{.Status}}'
```

## Handling Errors and Degraded Outputs

formatforge tools return a structured envelope. Read these fields before deciding the next action:

- **`ok: false`** — the tool call did not produce a usable artifact. Inspect `error.type` (e.g. `validation_error`, `missing_dependency`, `unsupported_input`) and `error.hints` (ordered list of remediation suggestions). Apply the first applicable hint; do NOT retry the same call unchanged.
- **`degraded: true`** — the artifact was produced but with reduced fidelity (e.g. fallback font, dropped feature, lossy table conversion). Inspect `degraded_reasons` (list of reason codes + descriptions). If the deliverable's audience can tolerate the degradation, accept and surface it to the user; otherwise re-call with `allow_degraded: false` to force a hard failure and address the root cause.
- **`source_needs_edit: true`** — the converter detected source-level issues that block clean output (e.g. malformed markdown table, unbalanced bracket, missing reference key). Run `lint_markdown` (or the format-specific linter) on the source, apply `autofix_markdown` for auto-fixable items, then re-convert. Do not bypass this signal.
- **`pre_conversion_lint.has_errors: true`** — `convert_markdown_to_docx` and related tools embed a lint summary. When errors are present, call `lint_markdown` directly to get the full issue list with line numbers; fix at source rather than guessing from the summary.

Never discard a `degraded` artifact silently — record the `degraded_reasons` in the user-facing report so the operator can decide whether to ship or rework.

## Heading Preflight (md→docx)

When converting markdown to docx, check `pre_conversion_lint.heading_advisory`
in the response:

- If `pattern == "single_leading_h1"` and no `reference_doc`:
  The converter auto-handles this (`title_from_first_h1='auto'`). No action needed.
- If `pattern == "single_leading_h1"` and `reference_doc` is set:
  Run `autofix_markdown` first to move H1 to YAML `title:`, then convert.
  The YAML title maps to Word "Title" style; sections starting at H1 map to
  "Heading 1" — aligning with typical reference DOCX expectations.
- If no `heading_advisory`: heading structure is already clean.

Prefer calling `lint_markdown` before `convert_markdown_to_docx` for documents
of unknown structure. The lint response `evidence` dict contains heading counts
for informed decision-making.

## Large-PDF Response Handling (pdf2md v0.5.1+)

The `pdf2md/convert_document_to_markdown_via_magic` MCP tool returns a workflow
result with ~60 QC report fields. Historically this could exceed ~1 MB on large
PDFs and break the OpenCode tool-confirmation dialog, silently
auto-cancelling the call.

**Default behavior (pdf2md ≥ 0.5.1):** the server now compacts the response by
default — summary fields (`markdown`, `stats`, `timings`, `quality_gate`,
`log_files`, and all `*_files` / `*_error` keys) are preserved verbatim; large
nested QC report bodies (`md_*_qc`, `md_*_autofix`, `md_*_patch_proposal`,
`ocr_suspicion` details) are auto-trimmed to keep the result under ~200 KB.
For any size of PDF, **call the MCP tool directly** — no preemptive CLI
fallback is needed.

**To inspect a trimmed report**: read the corresponding `*_files` path
(returned untrimmed in the response) with `read_file`.

**To receive the full uncompacted result** (rare; e.g. when the agent needs
all QC bodies inline for cross-section analysis): pass
`compact_response: false` to the tool call, or set
`PDF2MD_MCP_COMPACT_RESPONSE=0` in the server environment.

**CLI fallback** (rare — only when the MCP server itself is unavailable
or the agent must avoid the MCP confirmation dialog entirely):

```bash
python -m pdf2md.mcp_server.cli <pdf_path> [--mapping-strategy preserve]
```

The CLI writes the workflow result JSON to stdout; the `markdown` field
contains the absolute path of the produced `.md`. Run
`python -m pdf2md.mcp_server.cli --help` to confirm the entrypoint exists
in the target environment.

**Failure recovery:** if a `convert_document_to_markdown_via_magic` call still
returns a response that triggers auto-cancellation (e.g. running an older
pdf2md release), confirm the server version via `get_system_metrics` or by
checking the workspace `mcp_server/__init__.py`. Upgrade to ≥ 0.5.1 instead of
working around it with slicing — slicing breaks document-level QC.

## MCP Server Configuration (pdf2md v0.6.0+)

The `pdf2md` MCP server is a **single StreamableHTTP shim** with 8 tools (v0.6.1+):

| Transport | URL | Tools |
|-----------|-----|-------|
| **`streamableHttp`** | `http://127.0.0.1:8012/mcp` | All 8 tools below |

**Full toolset:**

| Tool | Purpose |
|------|---------|
| `convert_document_to_markdown` | Sync PDF→MD conversion (delegates to REST API `/convert`) |
| `convert_document_to_markdown_via_magic` | Alias for `convert_document_to_markdown` (backward compat) |
| `submit_conversion` | Async PDF→MD submission for large PDFs |
| `get_conversion_status` | Poll async task status |
| `get_conversion_result` | Retrieve completed async task result |
| `get_pdf2md_health` | Health status and queue metrics |
| `ocr_suspicion_scan` | Re-scan existing Markdown for OCR artifacts |
| `get_system_metrics` | psutil system diagnostics from backend |

**Tool selection guide:**
- **Small/medium PDFs (<20 pages)**: Use `pdf2md/convert_document_to_markdown` (or the `_via_magic` alias).
- **Large PDFs (≥20 pages)**: Use `pdf2md/submit_conversion` → poll `pdf2md/get_conversion_status` → retrieve `pdf2md/get_conversion_result`.
- **OCR suspicion re-scan** on existing Markdown: Use `pdf2md/ocr_suspicion_scan`.
- **Health/queue metrics**: Use `pdf2md/get_pdf2md_health`.

The server is backed by the `pdf2md-mcp-shim` Docker container
(`docker-compose.mcp-shim.yml`, port 8012). If tools return "does not
exist", ensure the container is running: `docker ps --filter name=pdf2md-mcp-shim`.
