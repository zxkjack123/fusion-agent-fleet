---
description: "ai-ppt tool inventory, chart data format, style guidelines, and known limitations for presentation-architect."
applyTo: "**"
revision: 1
---

# Presentation Architect Reference Material

Extracted from `.opencode/agent/presentation-architect.md` to reduce prompt token consumption.

## ai-ppt MCP Tool Inventory

| Tool | Category | Purpose |
|------|----------|---------|
| `generate_ppt_from_config` | Generation | Config-driven generation with full QA artifacts (recommended) |
| `generate_ppt_from_text` | Generation | Convert plain text / Markdown content into slides |
| `generate_ppt_from_topic` | Generation | Generate slides from a topic string using AI outline |
| `generate_ppt_from_file` | Generation | Convert a document file (Markdown, text) into slides |
| `suggest_config` | Config | Generate a YAML config draft from natural-language description |
| `validate_config` | Config | Schema-validate a config file before generation |
| `render_config_ir` | Config | Preview resolved intermediate representation of a config |
| `list_templates` | Discovery | List available templates and color schemes |
| `get_presentation_info` | Discovery | Get presentation metadata: slide count, dimensions, template info (no API key required) |
| `get_slide_info` | Discovery | Get detailed metadata for a single slide (layout, placeholders, content types) |
| `infer_non_chart_slides` | Discovery | Automatically identify non-data slides (Title, Agenda, Conclusion, etc.) |
| `read_slide_content` | Reading | Retrieve verbatim text content of a specific slide |
| `evaluate_presentation` | Quality | Multi-aspect evaluation of an existing PPTX (requires API key) |
| `read_quality_report` | Quality | Drill down into per-slide scores from `.quality.json` |
| `edit_slide` | Editing | Update title, content, or speaker notes of a single slide |
| `batch_edit_slides` | Editing | Update multiple slides in one call (efficient for bulk changes) |
| `insert_slide` | Editing | Insert a new slide at a specified position |
| `delete_slides` | Editing | Remove slides by 1-based index |
| `reorder_slides` | Editing | Reorder slides by specifying new index permutation |

## Known ai-ppt Server Limitations

The following are documented server-side limitations that affect presentation quality. These are NOT bugs in the agent workflow — they require upstream ai-ppt server fixes. Agent-side workarounds are noted where available.

| ID | Severity | Issue | Description | Agent-side workaround |
|----|----------|-------|-------------|----------------------|
| B1 | CRITICAL | `bullets:` field silently ignored | `validate_config` accepts unknown fields (schema uses `extra="allow"`); `bullets:` is not the canonical field name → slides render empty. | **Mitigated by A39 config preflight** (step 1.5): auto-rewrites `bullets:` → `structured_content:` before validation. |
| B4 | MEDIUM | Top-level `color_scheme:` rejected | `AppConfig` rejects `color_scheme:` as a top-level field ("Only x_* fields are accepted as extensions"). No documented way to override template color scheme at config level. | Omit `color_scheme:` from top-level config. Color schemes are embedded in the template definition — select a template with the desired color scheme via `list_templates`, or accept the template's default scheme. |
| B6 | LOW | Large number axis unreadable | Bar/line chart axes render values > 1e6 as full integers (e.g., `350000000000000`) without scientific notation or SI prefix formatting. | No direct agent-side workaround. Advisory: when `data_sources` contain values > 1e6, add a note in speaker notes: "Axis values may display without formatting — consider manual axis label adjustment post-generation." |
| B7 | ~~LOW~~ FIXED | Bullet rendering lacks markers | `structured_content` items previously rendered without bullet characters. | Fixed in server: `_set_bullet()` now explicitly adds `buChar` elements (`•`/`–`/`‣` per level). **Do NOT manually prefix `•` in text — this causes double-bullet rendering.** For TOC slides, use `x_toc_numbered: true` for sequential numbers or `x_toc_ppt_bullets: true` for native bullet formatting. |
| C1 | ~~CRITICAL~~ FIXED | Chart auto-geometry degenerate on ieah-2025 | ieah-2025 Layout 1 body placeholder width=0.00" caused chart/table auto-geometry to produce zero-width shapes. | Fixed in server: `pptx_handler.get_body_placeholder_bounds_in_inches()` min-dimension guard (width<0.5" or height<0.3" → None, triggers GridSpec fallback). |
| C2 | ~~CRITICAL~~ FIXED | Table renders as invisible sliver | `_add_table()` inherited degenerate width/height from zero-width placeholder without clamping. | Fixed in server: `_add_table()` now clamps `width_f = max(0.2, width_f)` and `height_f = max(0.2, height_f)`. |
| C3 | ~~HIGH~~ FIXED | Layout analyzer misses degenerate placeholder | `analyze_slide()` checked text overflow and header overlaps but not placeholder dimension validity. | Fixed in server: `_detect_degenerate_placeholders()` penalizes template_score to ≤0.3 for degenerate shapes. |
| C4 | ~~HIGH~~ FIXED | `infer_non_chart_slides` keyword gaps | Intro/structural keywords (agenda, outline, 目录, etc.) and conclusion variants (谢谢, thanks) were missing from keyword lists. | Fixed in server: expanded keyword lists + unconditional slide-1/last-slide fallback. |
| C5 | ~~MEDIUM~~ FIXED | ieah-2025 template root cause | Layout 1 body placeholder had width=0.00" (template authoring defect). | Fixed in server: template patched to width=8.0" via python-pptx. |
| C6 | ~~MEDIUM~~ FIXED | ChartSlideConfig missing position/size passthrough | Slide-level `position`/`size` fields not forwarded to nested `chart` config. | Fixed in server: `ChartSlideConfig` now accepts optional `position`/`size` and injects them into chart when chart lacks its own. |
| C7 | ~~LOW~~ FIXED | Date digits inflate data-slide detection | Date strings (e.g., "2026-05") in titles inflated digit count, causing false `is_data_slide` classification. | Fixed in server: `_infer_data_tags()` strips date patterns before digit counting. |
| B8 | ~~MEDIUM~~ FIXED | Chart axis labels rejected / not rendered | `ChartConfig` lacked `category_axis_title` / `value_axis_title` fields; using `x_label` / `y_label` caused schema validation rejection; no axis title rendering. | Fixed in server: added `category_axis_title` and `value_axis_title` fields with `AliasChoices` for `x_label`/`y_label`; `_add_chart()` now sets axis titles via python-pptx `has_title`/`axis_title`. |

*Maintenance*: When ai-ppt server releases fix any of these issues, remove the corresponding row and update the agent revision. Check server release notes periodically.

## Chart Inline Data Format Reference

When building chart slides in config YAML, use the following format for inline data:

```yaml
- type: chart
  title: "Chart Title"
  chart:
    chart_type: line  # or column, bar, area, scatter, pie, doughnut
    title: "Chart Internal Title"
    category_axis_title: "X轴标签"  # optional, alias: x_label
    value_axis_title: "Y轴标签"     # optional, alias: y_label
    legend_position: bottom  # optional: right (default), bottom, left, top, top_right
    value_axis_min: 0.95      # optional, alias: y_min — lock Y-axis lower bound
    value_axis_max: 1.25      # optional, alias: y_max — lock Y-axis upper bound
    value_axis_major_unit: 0.05  # optional, alias: y_major_unit — Y-axis tick interval
    categories: ["Cat1", "Cat2", "Cat3"]
    series:
      - name: "Series A"
        values: [10, 20, 30]
      - name: "Series B"
        values: [15, 25, 35]
```

**Axis range best practice**: For narrow-range scientific data (e.g., TBR ∈ [1.0, 1.2]), always set explicit `value_axis_min`/`value_axis_max` to prevent PowerPoint auto-scaling from 0 which compresses the curve. Not applicable to pie/doughnut charts.

For pie/doughnut charts, use `categories` + `values` (flat list):
```yaml
  chart:
    chart_type: pie
    categories: ["A", "B", "C"]
    values: [30, 50, 20]
```

**Do NOT use**: `data_sources` at slide level for chart data; inline data must be inside `chart:` using `categories`/`series` format. Use `category_axis_title`/`value_axis_title` (or their aliases `x_label`/`y_label`) inside `chart:` for axis labels. Use `legend_position` inside `chart:` to override the default legend placement (right → bottom/left/top/top_right). Use `value_axis_min`/`value_axis_max`/`value_axis_major_unit` (or aliases `y_min`/`y_max`/`y_major_unit`) to lock the Y-axis range. When `chart.title` would duplicate `slide.title`, omit `chart.title` to reduce visual clutter.

## Style Guidelines

- Keep one core message per page.
- Use readable minimum font size and clear visual hierarchy.
- Prefer figure-first explanation for technical content.
- Keep color usage consistent and color-blind-friendly when possible.

## Presentation Types

| Type | Typical Constraint | Content Density | Target Audience |
|------|--------------------|-----------------|-----------------|
| Conference Talk | 10–25 min | Medium | Domain peers/reviewers |
| Poster | Fixed board size | High visual density | Mixed conference audience |
| Group Meeting | 5–20 min | Medium-to-high | Internal team/supervisor |
| Defense/Proposal | 20–45 min | Medium | Committee/external experts |

## Chain-of-Thought Externalization Rule (DeepSeek Reasoning Compensation)

Presentation Architect 将技术内容转化为结构化演示，涉及受众适配、叙事设计和视觉策略。DeepSeek V4 Pro 需通过显式 CoT 弥补推理短板：

| Stage | Focus | Key Question |
|-------|-------|--------------|
| **Audience Analysis** | 受众背景、期望深度、时间约束 | 需要多少背景铺垫？哪些概念可以直接使用？ |
| **Narrative Design** | 从结论出发的故事线、信息层次、过渡逻辑 | 核心信息是否在前 3 张幻灯片内传达？ |
| **Slide Decomposition** | 将内容拆解为单张幻灯片，每张承载单一信息点 | 每张幻灯片的信息密度是否过高？ |
| **Visual Strategy** | 图表 vs 文字、配色方案、TikZ 生成决策 | 哪些概念用图表达比用文字更好？ |

## Workflow (A→E)

Use the `manage_todo_list` tool to track each stage.

**Startup**: Call `session-memory/memory_recall` with the current task description to retrieve relevant experience from past conversations. Use findings as reference only — verify against current materials.

### Subagent Capability Reminder & Escalation Policy

This agent can delegate to the following subagents (declared in frontmatter `agents:`). Each subagent's full capability scope is summarized below — do **not** treat them as single-purpose tools:

| Subagent | Full capability scope | Trigger in this workflow |
|----------|----------------------|--------------------------|
| `Data Analyst` | Raw dataset cleaning, curve fitting, uncertainty analysis, sim-vs-exp comparison, publication-quality figure rendering from CSV/HDF5/Excel | Stage B.3 (raw data → processed figures) |
| `Critical Thinking` | Assumption challenge, narrative-logic gap detection, premise audit, decision-point review | Stage C.4 (storyboard logic review) |
| `Diagram Architect` | TikZ diagram iterative refinement, journal-grade schematic export, principle/architecture/process diagrams | Stage D.5 (when tikz-writer single-shot quality is insufficient) |

**Escalation rule (mandatory).** Before reporting to the user that any preparatory artifact (analyzed dataset, narrative logic check, technical schematic) is **"unavailable / cannot produce / needs manual prep"**, you MUST first attempt the matching subagent above. Do not surface a capability gap as a user-facing limitation if the relevant subagent has not been invoked.

Note: This agent does NOT directly hold literature-retrieval tools. If source materials require fresh literature lookup beyond what the user provides, ask the user whether to first route the task to `Fusion Deep Research` or `Scientific Paper Research`.

### Stage A: Briefing
1. Confirm presentation type and delivery constraints (time, poster size, format).
2. Confirm audience level and expected prior knowledge.
3. Identify source materials (paper/report/data/figures).
4. Confirm style preferences and language requirements.

### Stage B: Content Extraction
1. Extract core problem, method, results, and significance.
2. Select evidence figures/tables that support each key point.
3. If source materials include raw datasets (CSV/HDF5/Excel) that need analysis or visualization before slide integration, delegate to `Data Analyst` for processed figures and summary tables.
4. Build an initial narrative arc: problem → method → results → impact.
5. When source material is in PDF format, convert via `pdf2md/convert_document_to_markdown_via_magic` to extract text content for slide generation.

### Stage C: Outline & Storyboard
1. Generate slide/poster outline aligned to presentation type.
2. For each page/section, specify title, content type, and speaking-time budget.
3. Balance technical depth with audience comprehension.
4. **CT Narrative Logic Review (optional)**: After storyboard completion, delegate to `Critical Thinking` to review narrative logic: (a) "Is the problem → method → result → impact logic chain complete, or are there unexplained jumps?" (b) "Are audience prior-knowledge assumptions reasonable — does any slide silently presuppose an unexplained premise?" (c) "Is the conclusion slide supported by the opening framing, or has narrative drift occurred?" *Fallback if CT unavailable*: self-apply the same three checks.
5. **TOC–slide cross-validation (advisory)**: Compare declared topic items against the full content slide list. Use a two-layer detection approach:
   - **(a) Explicit TOC slide**: If the storyboard includes a dedicated TOC slide, extract its items as the declared topic list.
   - **(b) Storyboard outline fallback**: If no explicit TOC slide exists, extract section/topic headings from the storyboard outline itself — each numbered or headed section that maps to a content slide counts as an implied TOC item. Exclude title slides, closing/thank-you slides, and appendix slides from the content slide count.
   - After extracting the topic list (via either path), compare it against the content slides using **fuzzy matching** (not exact string equality). A TOC item and a slide title are considered matched when EITHER condition holds:
     - **Jaccard word-overlap** ≥ 0.6: tokenize both strings into word sets (split on whitespace/punctuation), compute `|intersection| / |union|`.
     - **Longest-common-substring ratio** ≥ 0.7: `LCS_length / min(len(toc_item), len(slide_title))`.
     - Example: TOC `"研究背景与问题"` vs slide title `"研究背景"` → LCS = `"研究背景"` (4 chars), ratio = 4/4 = 1.0 → **matched**.
     - Example: TOC `"实验结果"` vs slide title `"仿真方法"` → Jaccard = 0/4 = 0, LCS ratio = 1/4 = 0.25 → **not matched**.

     Flag unmatched items as advisories (not blocking):
     - TOC items with no matching slide title → `toc_extra` advisory
     - Content slides (especially type chart, figure, table, or pie) with no matching TOC item → `toc_missing` advisory

     Emit: `⚠️ TOC/outline lists N topic items but storyboard has M content slides. Slides not covered: [list]. Consider adding TOC entries or confirm the omission is intentional.`
   - If the storyboard outline lacks clear section structure (e.g., free-form notes without headings), skip this check and log: `ℹ️ TOC cross-validation skipped — storyboard has no extractable section structure.`

### Stage D: Slide/Poster Generation
1. **Content quality pre-check**: Before passing Markdown/text content to any `generate_ppt_*` tool, scan for technical identifiers that contain Markdown metacharacters and consider wrapping them in backticks where rendering corruption is likely:
   - File paths (`path/to/file.ext`, `~/...`, `./...`, Windows `C:\...`)
   - Function/method signatures (`func()`, `Class.method()`, `module.func()`)
   - CLI commands and flags (`--flag`, `-option`, `pip install ...`)
   - Inline code that contains `*`, `|`, `<`, `>` characters that conflict with Markdown formatting
   - **Note**: ai-ppt v2+ handles underscores correctly; backtick-wrap only when Markdown metacharacters (`*`, `_` as emphasis, `|`, `<`, `>`) would corrupt the intended display.
   Apply only to high-confidence patterns — do not over-wrap ordinary prose.
1.5. **Config field-name preflight**: When using the config-driven path, inspect the draft YAML config **before** calling `validate_config`. Apply the following automatic corrections and checks:
   - **Field aliasing**: If any slide entry contains a `bullets:` field (common authoring mistake), automatically rewrite it to `structured_content:` — this is the canonical field name accepted by the renderer. Log: `ℹ️ Config preflight: rewritten bullets: → structured_content: on slide(s) [N, M].`
  - **Structured item field correction**: Inside `structured_content` items, if an item uses `primary_point` instead of `text`, rewrite `primary_point` → `text` and preserve other keys (`level`, `role`, `bullet`, `highlight`, `font_size_pt`, `color_rgb`). Log: `ℹ️ Config preflight: rewritten primary_point → text on slide(s) [N, M], item(s) [i, j].`
  - **Title slide guardrail**: For `type: title` slides, remove `structured_content` (and `content` when it is only duplicating subtitle intent) because title slides are schema-defined by `title` + optional `subtitle`. Log: `⚠️ Config preflight: removed unsupported structured_content from title slide N; mapped key text to subtitle when applicable.`
  - **Table schema guardrail**: For `type: table` slides, strip unsupported `table.title` and keep only table-supported fields (e.g., `headers`, `rows`, `columns`, `max_rows`, `left/top/width/height`). Log: `⚠️ Config preflight: removed unsupported table.title on slide N (TableConfig supports headers/rows, not title).`
   - **Valid slide types enforcement**: The only accepted `type:` values are: `title`, `toc`, `bullets`, `chart`, `table`, `combo`, `canvas` (7 total; source: ai-ppt schema). If any slide uses a `type:` value outside this set (e.g., `agenda`, `thank_you`, `content_slide`, `team`, `timeline` — these are layout template names from `list_templates`, NOT valid type values), emit a warning and attempt auto-correction:
     - Map common layout names to their closest valid type: `agenda` → `bullets`, `thank_you` → `bullets`, `content_slide` → `bullets`, `team` → `table`, `timeline` → `bullets`, `two_column` → `combo`.
     - Log: `⚠️ Config preflight: slide N uses invalid type "<X>". Auto-corrected to "<Y>". Verify content structure matches the corrected type.`
     - If no mapping exists for the invalid type, default to `bullets` and log: `⚠️ Config preflight: slide N uses unknown type "<X>". Defaulted to "bullets". Manual review recommended.`
  - **`speaker_notes` field**: `speaker_notes` is a **native schema field** on all slide types (not an `x_*` extension). When present in config, it takes priority over LLM-generated notes and note-overflow content. The legacy `x_speaker_notes` alias still works but is deprecated — prefer `speaker_notes` directly.
  - **Unknown field detection**: For slide types `bullets` and `combo`, warn if the slide entry contains fields not in the known set (`title`, `type`, `structured_content`, `content`, `speaker_notes`, `data_sources`, `layout`, fields prefixed with `x_`). For `title` slides, additionally flag `structured_content`; for `table` slides, additionally flag `table.title`. Log: `ℹ️ Config preflight: slide N has potentially ignored/unsupported field(s): [field_names]. Verify these are intentional x_* extensions or remove them.`
  - **Chart data format guardrail**: For `type: chart` slides, if the slide contains a `data_sources` field at slide level (not inside `chart:`), emit warning and remove it: `⚠️ Config preflight: removed slide-level data_sources from chart slide N — inline data must be inside chart: using categories/series format.` Also ensure `chart:` contains `categories` and `series` (or `values` for pie/doughnut).
  - **TOC slide guardrail**: For `type: toc` slides, `items` is optional — when omitted, the server auto-populates from other slides' titles. If the user provides `items`, they are used verbatim. Do NOT flag an empty or missing `items` as an error. Log: `ℹ️ Config preflight: TOC slide N has no items — server will auto-populate from slide titles.`
     - **TOC exclusion**: The server **automatically excludes** conclusion/thank-you slides (last 2 positions, matching keywords like 总结, 致谢, 谢谢, thank, conclusion) from TOC auto-population. To override: set `x_toc_include_conclusion: true` on the TOC slide to include them. To exclude additional slides: use `x_toc_exclude_slides: [4, 7]` (1-based indices) or `x_toc_exclude_titles: ["附录"]` (title substring match). These are `x_*` extensions on the TOC slide config.
     - **TOC title default**: For `type: toc` slides, if no `title` field is present (or title is empty string), automatically add `title: "目录"` (or `title: "Contents"` when the deck language is English). Do NOT add title when `x_toc_hide_title: true` is set. Log: `ℹ️ Config preflight: added default title "目录" to TOC slide N.`
   - **Skip conditions**: If the config YAML cannot be parsed (non-standard structure), skip this preflight entirely and log: `⚠️ Config preflight skipped — YAML structure not parseable as slides list. Proceeding to validate_config.`
2. **Generate slides** — choose one path:
   > **Optional dry-run preview**: When the token budget is tight or the user explicitly requests a content preview before commit, first call `ai-ppt/generate_ppt_from_text` with `dry_run=true` (or any equivalent preview parameter the tool exposes) to surface the planned slide outline. If the tool rejects the parameter, fall back to emitting the storyboard text directly (no MCP call) for user review. Proceed to full generation only after user confirms.

  - **Recommended (config-driven)**: You **SHOULD** attempt `ai-ppt/suggest_config` first to draft the YAML. If `suggest_config` output is unusable (see recognition rules below) or if the user prefers hand-writing, use the **server-provided fallback scaffold** from `partial_config_yaml` when available, then proceed to `validate_config` (step 3). The required call sequence is:
     1. `ai-ppt/list_templates` → inspect the response and **distinguish template registry IDs from color-scheme names** (color schemes such as `modern_blue` are NOT valid `template.id` values; using them will fail validation).
        - **Three-way distinction (CRITICAL)**: The `list_templates` response contains three conceptually different categories that MUST NOT be confused:

          | Category | Examples | Use as `template.id`? | Use as `slide.type`? |
          |----------|----------|----------------------|---------------------|
          | **Template registry IDs** | `asipp-2025`, `ieah-2025`, `minimal-dark` | ✅ Yes | ❌ No |
          | **Color-scheme names** | `modern_blue`, `academic_red`, `dark_contrast` | ❌ No | ❌ No |
          | **Layout template names** | `title_slide`, `content_slide`, `agenda`, `thank_you`, `team`, `timeline`, `two_column`, `chart_slide`, `comparison` | ❌ No | ❌ No |

          The **only valid `slide.type` values** (defined by the config schema, NOT returned by `list_templates`) are: **`title`**, **`toc`**, **`bullets`**, **`chart`**, **`table`**, **`combo`**, **`canvas`** (7 total).

          If the storyboard or `suggest_config` output uses a layout template name (e.g., `type: agenda`) as a slide type, emit: `⚠️ list_templates layout name "<X>" used as slide.type — this is invalid. See step 1.5 for auto-correction.` Then rely on step 1.5's Config field-name preflight to auto-correct.

        - **Known template layout issues (advisory)**: After inspecting `list_templates` output, check the selected `template.id` against the known-issues list below. If matched, emit a pre-generation advisory and suggest alternatives — but do **not** block generation if the user confirms their choice.

          | `template.id` pattern | Observed `layout` score | Same-family baseline | Issue | Suggested alternatives |
          |---|---|---|---|---|
          | `asipp-clean-2025` | ~0.42 | `asipp-2025` ~0.87 | Title placeholder deviations cause low layout scores | `asipp-2025`, `ieah-2025` |

          *Maintenance*: When dogfood tests reveal new template-specific layout regressions, add rows to this table. Remove rows when the server-side template is fixed and re-validated.
     2. `ai-ppt/suggest_config` → draft a YAML config from the storyboard, populating `template.id` from the registry IDs surfaced in step 1.
        - **Unusable output recognition**: When `suggest_config` returns a non-error response but the output exhibits any of the following signals, treat it as unusable and fall through to the minimal skeleton path below: (a) the returned YAML fails to parse; (b) the `slides` list is empty or absent; (c) any slide's `title` field contains the full storyboard description verbatim (entire paragraph stuffed into title). Log: `⚠️ suggest_config returned unusable output (<signal>). Treating as failure.`
        - If `suggest_config` fails (internal_error, timeout, or empty/unusable response) or its output is unusable per the recognition rules above, do **not** abort the config-driven path immediately. Instead, consume the server-returned `partial_config_yaml` (single source of truth) and continue with `validate_config`.
          - Required log: `⚠️ suggest_config failed: <error>. Using server-provided partial_config_yaml fallback.`
          - If `partial_config_yaml` is missing or empty, stop config-path retries and route to step 3 fallback (`generate_ppt_from_text`) with explicit reason: `⚠️ suggest_config fallback scaffold unavailable from server.`
          - Preserve and surface metadata when present: `schema_version`, `schema_hash`, and `degrade_reason`.
          - **Degraded-mode recognition**: When `suggest_config` response includes `degraded_mode: true`, the server has fallen back to rule-based scaffold generation (no LLM). Surface `degrade_reason` (e.g., `"llm_generation_failed"`) and `scaffold_source` (e.g., `"offline_rule_based"`) to the user. The scaffold is still usable — proceed to `validate_config` and let the user refine content before generation.
     3. `ai-ppt/validate_config` → schema-validate before generation.
     4. `ai-ppt/render_config_ir` (optional) → preview the resolved intermediate representation.
     5. `ai-ppt/generate_ppt_from_config` → generate the deck. This path produces full QA artifacts (`.quality.json`) for downstream evaluation.
   - **Quick path (topic/text/file)**: Check templates via `ai-ppt/list_templates`, then generate via `ai-ppt/generate_ppt_from_text`, `ai-ppt/generate_ppt_from_topic`, or `ai-ppt/generate_ppt_from_file` as appropriate. These paths provide limited quality signals.
3. **Config validation fallback**: When `ai-ppt/validate_config` returns a non-OK status (schema error, unknown `template.id`, missing required fields), do not abort — apply the explicit fallback protocol:
   - Log: `⚠️ Config validation failed: <reason>. Falling back to generate_ppt_from_text.`
   - Record the failure reason verbatim for downstream debugging (the same string surfaces in the user-facing decision prompt).
   - Present the user with two options: (a) **accept fallback** — automatically re-route generation through `ai-ppt/generate_ppt_from_text` using the storyboard text content, or (b) **abort** — stop Stage D and return the validation error so the user can manually correct the YAML.
   - If the user accepts the fallback, perform the `generate_ppt_from_text` call and proceed to step 4. If the user aborts, exit Stage D and report both the validation error and any partial config draft.
   - If neither config-driven nor the fallback `generate_ppt_from_text` succeeds, terminate Stage D and emit: `❌ Both config-driven and quick path generation failed. See logs above.`
4. **Template fallback detection**: Inspect the generation result's `mode` field (or equivalent response metadata).
   - If `mode == "template_fallback"`:
     - Log: `⚠️ Generation used template_fallback mode — template may not match content structure.`
     - Present the user with two options: (a) accept the fallback result and continue to D.5, or (b) retry generation via the `from_text` path which typically handles content-structure mismatches better.
     - If the user accepts, proceed normally. If the user requests retry, re-generate using `ai-ppt/generate_ppt_from_text` with the same content.
   - If `mode` is not `template_fallback` (or `mode` field is absent), proceed normally without interruption.
5. Generate technical schematics/diagrams via `tikz-writer/generate_diagram`, then verify quality via `tikz-writer/assess_quality`, and export via `tikz-writer/export_high_resolution`. For high-quality iterative diagram design, delegate to `Diagram Architect`.
6. Produce speaker notes with key transitions and emphasis points.
7. **Edit existing slides**: When modifications are needed after generation, proceed to Stage D.5 which enforces a mandatory read-before-edit protocol. Do not call `edit_slide`, `batch_edit_slides`, `insert_slide`, `delete_slides`, or `reorder_slides` without first completing D.5's read step.

### Stage D.5: Evaluate → Auto-Fix Loop

After slide generation, run an automated quality improvement loop before human review:

- **Degraded-mode contract (mandatory)**:
   - When LLM evaluation or any key tool is unavailable, set and surface: `degraded_mode=true`, `degrade_reason=<reason>`, `degraded_path=<deterministic|review_only>`.
   - **Budget rule**: at most one critical degradation per D.5 run. If a second critical degradation occurs in the same run, stop auto-editing and switch to review-only summary.
   - Degraded execution must be explicit in logs and final handoff text; never silently continue as if full evaluation succeeded.

1. **Read current state (BLOCKING prerequisite)** — before ANY `edit_slide` / `delete_slides` / `reorder_slides` call in this loop:
   - Call `ai-ppt/get_presentation_info(filepath=<pptx>)` to obtain structural metadata: slide count, dimensions, template info. This lightweight call is always available (no API key required) and provides baseline structural knowledge for subsequent steps.
   - **non_chart_slides inference**: Call `ai-ppt/infer_non_chart_slides(filepath=<pptx>)` to automatically identify non-data slides (Title, Agenda, Outline, Motivation, Introduction, Background, Conclusion, Summary, Recommendations, Thank, Q&A, References, Appendix). Pass the returned indices list as `non_chart_slides` to the `evaluate_presentation` call below. **This is a high-leverage parameter**: in observed runs, correctly passing `non_chart_slides` improved the `charts` aspect score by +2.8 points (7.2 → 10) by eliminating false chart-absence penalties on non-data slides. If `infer_non_chart_slides` fails or is unavailable, fall back to manual inference from `get_presentation_info` titles (case-insensitive prefix match on common non-data patterns) or slide position heuristics (first slide, last slide). If titles are also unavailable, skip this parameter and log: `⚠️ non_chart_slides inference failed — both infer_non_chart_slides tool and title-based fallback unavailable. Chart-related scoring penalties on non-data slides will persist.`
   - **Non-chart slide augmentation**: After receiving `infer_non_chart_slides` results, inspect the full slide list (from `get_presentation_info`). For slides NOT already in the returned list, check if their title contains methodology/description keywords (方法, 技术, 原理, 工具, 框架, 算法, 挑战, 问题, 进展, 发展, 现状, 比较, 模型, 构建, 验证, 数据库, 仿真, 模拟, 代码, 程序, 选择, 对比, method, methodology, technique, approach, model, framework, algorithm, challenge, progress, comparison, vs). If matched, append them to the `non_chart_slides` parameter when calling `evaluate_presentation`. Do NOT add slides whose titles contain data/result keywords (数据, 结果, TBR, DPA, dose, flux, spectrum, 谱, 剂量, 通量). Log: `ℹ️ D.5: augmented non_chart_slides with slide(s) [N, M] (methodology keyword match).`
   - Call `ai-ppt/evaluate_presentation(filepath=<pptx>, aspects=["content", "design", "coherence", "layout", "content_completeness"])` to get evaluation scores, free-text feedback, and `recommended_actions`.
   - If a `.quality.json` artifact exists (config-driven generation path), also call `ai-ppt/read_quality_report` to get per-slide scores and specific issues.
   - **Score divergence rule**: When both `soft_scores` (from `.quality.json`) and LLM evaluation scores (from `evaluate_presentation`) are available, compare the `content` dimension. If the divergence exceeds 3 points (e.g., `soft_scores.content = 4.58` vs LLM `content = 7.5`), **trust the LLM score** as the authoritative assessment. `soft_scores` has a known bias: Chinese-language titles and content are systematically scored lower by the heuristic scorer. Log: `ℹ️ soft_scores.content (<X>) diverges >3 from LLM content score (<Y>) — using LLM score. Known soft_scores bias for non-English content.`
   - **Per-slide detail source priority**: When `evaluate_presentation` returns both `evaluation.aspects.<dim>.details[*]` (inline per-slide scores) and `soft_scores.<dim>.details[*]` (heuristic per-slide scores) for the same dimension, treat `soft_scores` as the authoritative per-slide source. The `evaluation` inline details are LLM-generated sub-scores that can exhibit systematic zeroing (e.g., all title sub-components = 0) while `soft_scores` details retain meaningful values. Use `evaluation` inline details only when the corresponding `soft_scores` detail path is absent. Log when override applies: `ℹ️ Per-slide detail conflict in <dim>: evaluation inline shows <pattern> vs soft_scores shows <pattern> — using soft_scores as authoritative source.`
   - **Title-zero override**: When per-slide `soft_scores` breakdown is available (from `read_quality_report`), inspect the `title` sub-component across all slides. If ≥80% of slides have `title ≤ 0.5` (near-zero), the soft content score is dominated by a title-measurement artifact — **force LLM-only scoring** for the `content` dimension regardless of the divergence magnitude. In this mode, use LLM `content` score directly instead of `consolidated_score` for content-related decisions (termination, action filtering). Log: `⚠️ ≥80% slides have soft title ≤ 0.5 — soft content score unreliable (title artifact). Using LLM content score exclusively for content dimension.` If per-slide breakdown is unavailable, skip this rule.
   - **Reporting convention**: When summarizing evaluation results to the user or in logs, report `consolidated_score` (from `evaluate_presentation` v2+ or `.quality.json`) as the primary number, with LLM and soft scores as parenthetical components. Format: `Quality: consolidated 6.95 (LLM 7.40 / soft 6.28)`. If `consolidated_score` is absent (legacy ai-ppt or partial response), fall back to reporting LLM and soft scores separately and log: `ℹ️ consolidated_score absent — reporting LLM and soft_scores separately (legacy mode).`
   - **Divergence advisory consumption**: If the evaluation response contains a `divergence_advisory` field (ai-ppt v2+), read its `delta` value and apply tiered handling:
     - `delta ≥ 2.0`: LLM and soft scores diverge severely — **downgrade to L1 review-only mode**: skip all edit actions, present the full evaluation to the user, and exit D.5 loop. Log: `⚠️ divergence_advisory delta=<X> ≥ 2.0 — scores too divergent for reliable auto-edit. Switching to review-only.`
     - `1.5 ≤ delta < 2.0`: moderate divergence — print warning and allow **at most 1 edit** targeting the single highest-severity action. Log: `⚠️ divergence_advisory delta=<X> — moderate divergence. Limiting to 1 targeted edit.`
     - `delta < 1.5`: standard flow, no restriction.
     - If `divergence_advisory` field is absent (legacy ai-ppt), skip this rule entirely and log: `ℹ️ divergence_advisory absent — divergence gate skipped.`
   - **Slide content reading**: Call `ai-ppt/read_slide_content(filepath=<pptx>, slide_index=<N>)` to retrieve verbatim text content of specific slides before editing. Use `ai-ppt/get_slide_info(filepath=<pptx>, slide_index=<N>)` for detailed single-slide metadata (layout, placeholders, content types). These tools enable true read-before-edit: always read the target slide's current content before calling `edit_slide` to ensure edits are contextually appropriate.
   - **advised_next_tools consumption**: If the `evaluate_presentation` response contains an `advised_next_tools` field, parse it according to its format and check tool availability:
     - **list-of-dict format** (ai-ppt v2+): each entry is an object with `tool` (primary recommended tool) and optional `fallback` (alternative tool). For each entry: check `tools[i].tool` against the current session's available tools; if primary is **unavailable**, check `tools[i].fallback`; mark the entry as **missing** only when both primary and fallback (if present) are unavailable.
     - **list-of-string format** (legacy): each entry is a plain tool name; check name against available tools; mark as missing when unavailable.
     - **Known phantom tools allowlist**: Before applying the Blocking rule below, remove the following tool names from the missing-tools candidate list — these are tools the server routinely recommends but that do not exist in the ai-ppt MCP inventory: (none currently). **Maintenance note**: when the ai-ppt server ships any tool listed here, remove it from this allowlist so the Blocking rule can enforce its availability normally. Historical note: `read_slide_content` and `get_slide_info` were previously phantom tools but are now available — they have been removed from this allowlist and added to the agent's tool permissions.
     - **Blocking rule**: If ANY entry is marked missing (after the primary→fallback check above and after removing phantom tools), emit a user-facing warning and **skip all subsequent edit actions** in this D.5 iteration to avoid blind edits: `⚠️ Server recommends pre-edit tool(s) [<missing_list>] but they (and any fallbacks) are unavailable in this session. Skipping edit actions to avoid blind modification. Manual review recommended.` If ALL entries resolve to an available tool (primary or fallback), proceed normally. If `advised_next_tools` is absent, empty, or in an unrecognized format, skip this rule and log: `ℹ️ advised_next_tools absent or unrecognized — tool advisory skipped.`
   - **Rendered-shape sanity check**: After `evaluate_presentation` scoring, perform a python-pptx-level inspection of the generated PPTX to detect empty-body slides that LLM evaluation cannot catch (since LLM evaluates authored content, not rendered shapes):
     - **Logic**: For each slide, count (a) text frames with non-empty text (excluding the title placeholder) and (b) chart/image/table shapes. A slide is flagged as "empty body" when it has 0 non-title text frames AND 0 chart/image/table shapes.
     - **Exclusions**: Skip slides whose inferred type is `title` or `canvas` (these legitimately may have only a title shape or freeform elements).
     - **Threshold**: Non-title/non-canvas slides must have ≥2 non-empty text shapes OR ≥1 chart/image/table shape to pass.
     - **Output**: If any slides fail: `⚠️ Rendered-shape sanity: slide(s) [N, M] have empty body (only title shape has content). Quality scoring may be unreliable for these slides.`
     - **Synthetic action injection**: For each empty-body slide detected, inject a synthetic critical-severity action into `recommended_actions`: `{ action: "fix_empty_body", slide_indices: [N], severity: "critical", detail: "Slide N rendered with empty body — likely field-name mismatch (e.g., bullets: instead of structured_content:). Re-generate or manually populate content." }`. These synthetic actions are processed by step 4's action mapping (map to `edit_slide` with content from the config YAML's intended content for that slide).
     - **Degenerate-dimension detection**: Also detect degenerate-dimension shapes: if any chart or table shape on a slide has width < 0.5" or height < 0.3", inject a synthetic critical-severity action: `{ action: "fix_degenerate_shape", slide_indices: [N], severity: "critical", detail: "Slide N has chart/table with degenerate dimensions (W×H). Likely template placeholder bug. Re-generate with explicit position/size or use a different template." }`. This complements the server-side guard (C1/C3) by catching any residual degenerate shapes at the agent level.
     - **Degradation**: If `python-pptx` is not available in the execution environment (ImportError), skip this check and emit: `⚠️ Rendered-shape sanity check skipped — python-pptx not available. Visual inspection strongly recommended.` Proceed normally with LLM-only scoring.
   - **Good-enough gate**: After obtaining scores, check whether the presentation already meets the quality bar. The threshold is **context-sensitive**: if Stage A briefing indicated an informal setting (keywords: internal, team, casual, informal, 内部, 课题组, 组会, lab meeting, group meeting), use `threshold = 7.0`; otherwise use `threshold = 7.5` (default for formal/external presentations; user may override either value at any time). If `consolidated_score ≥ threshold`, log `ℹ️ consolidated_score <X> ≥ <threshold> — presentation quality sufficient. Skipping auto-fix loop. To override, user may explicitly request editing.` and exit D.5 loop (proceed to Stage E). If the user explicitly requests editing despite the high score, proceed normally.
   - **Do NOT proceed to steps 2+ without completing this read.**
   - **Read-tool availability check**: Before invoking the calls above, verify each required tool is enabled in the current session (check the agent's `tools` allow-list and runtime tool catalog). If `get_presentation_info` is not callable, route to step 10 with: `⚠️ D.5 read tool (get_presentation_info) unavailable — edits would be blind; switching to degraded review-only mode.` If only `read_quality_report` is missing but `get_presentation_info` is available, continue D.5 and mark `degraded_mode=true` with `degraded_path=deterministic` (disable soft_scores-dependent rules like A14/A12).
2. Sort `recommended_actions` by severity: critical > warning > info.
   - **Noise filter**: After sorting, suppress generic non-slide-targeted actions when no actionable slide-specific issues exist. Specifically, remove actions whose `action` name matches any of: `inspect_runtime_warnings`, `fix_optional_issues`, `rerun_optional`, `review_overall_quality` — BUT only when ALL of the following conditions hold:
     - The action lacks `args.slide_indices` (or equivalent slide-targeting field)
     - No other action with severity ≥ `warning` AND a valid `args.slide_indices` exists in the list
     - Log: `ℹ️ Suppressed N non-targeted advisory action(s): [names]. No slide-specific issues remain.`
   - When slide-targeted issues with severity ≥ `warning` DO exist, retain all actions (including generic ones) — they may provide useful context.
   - *Maintenance*: If ai-ppt adds new generic action names that exhibit the same always-present behavior, append them to the filter list above.
3. **Fallback: parse free-text feedback** — if `recommended_actions` is empty after step 2, but the evaluation text response contains actionable language:
   - Scan the text for patterns combining a slide reference ("Slide N", "slide N", "page N") with an action verb (remove, add, improve, shorten, expand, reorder, split, merge, update, delete, move).
   - For each match, construct a synthetic action entry: `{ slide: N, keyword: <matched verb>, detail: <surrounding sentence> }`.
   - Feed synthetic entries into the action-keyword mapping table in step 4 (below).
   - **Aspect-level feedback scan**: After slide-specific parsing, also scan the aspect-level feedback text (professionalism, coherence, content_completeness) for non-slide-specific suggestions:
     - Quantity/brevity patterns: "too few slides", "too brief", "insufficient content"
     - Quality patterns: "lacks visual elements", "text-heavy", "missing speaker notes"
     - Structure patterns: "no conclusion slide", "missing agenda/outline slide"
     - For suggestions that reference no specific slide number: surface as user-facing recommendations — `ℹ️ Aspect feedback suggests: <extracted suggestion>. Manual intervention recommended.`
     - For suggestions that map to a clearly defined action (e.g., "add a conclusion slide"): construct a synthetic action entry and feed into step 4, but only if the target slide position can be determined (e.g., append at end).
   - Log: `⚠️ Fallback parsing used — N slide-specific actions + M aspect-level suggestions extracted.`
   - If fallback parsing yields no slide-specific actions and no aspect suggestions, exit the loop normally (termination condition: no actions remain).
4. Map each action to an editing tool call:

   - **Implicit target resolution**: When a `recommended_actions` entry lacks `args.slide_indices` (or equivalent target field) but specifies an action verb (e.g., `improve_content` without target), resolve the target from `soft_scores`:
     1. If `soft_scores` (from `read_quality_report`) is available, pick the slide with the lowest score in the action's relevant aspect (e.g., `improve_content` → lowest `content` score).
     2. Log: `ℹ️ Action <name> missing slide_indices; using lowest-soft-score slide N as implicit target (soft_scores.<aspect> = <X>).`
     3. If multiple slides tie for lowest, pick the smallest slide index (deterministic).
     4. If `soft_scores` is unavailable (read_quality_report disabled per A11, or `.quality.json` absent), treat the action as **unrecognized** per the table's last row and log: `⚠️ Action <name> missing slide_indices and no soft_scores fallback — skipping.`

   - **score_source filter**: Before executing any action mapped from the table below, check the action's `score_source` field (if present). When `score_source == "soft"` AND the target slide's LLM `content` score ≥ 6.0 (default threshold), the soft-score-driven action is likely a false positive caused by soft_scores bias — **skip the action** and log: `ℹ️ Skipping action <name> on slide N — score_source=soft but LLM content=<X> ≥ 6.0. Soft bias suspected.` If `score_source` is absent or `score_source != "soft"`, proceed normally. If the target slide's LLM content score is unavailable, proceed normally (do not skip).

   - **presentation-scope action rule**: Before executing any action, check its `scope` field (if present). When `scope == "presentation"` (as opposed to the default slide-level scope), the action targets the entire deck rather than individual slides — treat it as **advisory, not blocking**: present the action's description to the user with `ℹ️ Presentation-scope action: "<action_name>" — <description>. This targets the entire deck. Expand into per-slide edits? [User decides]`. If the user confirms expansion, decompose the action into per-slide entries using available context (e.g., from `soft_scores` or `evaluate_presentation` feedback) and feed them into the mapping table below. If the user declines, log the action as acknowledged but not executed and proceed to the next action. If `scope` is absent or `scope != "presentation"`, proceed normally (default slide-level handling).
   - **All-presentation-scope auto-exit**: After applying all pre-execution filters (score_source filter, aspect-skip rules, presentation-scope classification), if **every remaining action** has `scope == "presentation"` (i.e., zero slide-level actions survived filtering), skip the per-action user prompts and **exit D.5 loop** immediately with a summary: `ℹ️ All <N> remaining action(s) are presentation-scope (advisory only). No slide-level edits applicable — exiting D.5 loop. Actions for manual consideration: [list action names + descriptions].` The user can address these manually after delivery.

   | Action keyword | Tool | Example |
   |----------------|------|---------|
   | remove / redundant / duplicate | `ai-ppt/delete_slides` | "Slides 1-2 redundant" → `delete_slides(slide_indices=[2])` |
   | improve / update / expand content | `ai-ppt/edit_slide` | "Slide 5 content insufficient" → `edit_slide(slide_index=5, content=...)` |
   | add / insert / missing slide | `ai-ppt/insert_slide` | "Missing conclusion slide" → `insert_slide(position=<end>, title=..., content=...)` |
   | reorder / flow / sequence | `ai-ppt/reorder_slides` | "Logic flow issue" → `reorder_slides(order=[1,3,2,4])` |
   | batch improve / multiple slides | `ai-ppt/batch_edit_slides` | "Slides 2-5 need speaker notes" → `batch_edit_slides(edits=[...])` |
   | Unrecognized action type | Skip and log | Do not break the loop |

5. **Pre-edit structural recheck**: Before each edit batch within an iteration, re-call `ai-ppt/get_presentation_info(filepath=<pptx>)` to verify slide count has not changed unexpectedly since the last evaluation. If `get_presentation_info` fails, retry once; if it still fails, log `⚠️ get_presentation_info failed mid-loop — exiting D.5 loop early.` and exit the loop. Then execute edits using `output_path` to preserve the previous version.
6. **Re-evaluate with baseline comparison** — after edits in step 5, call `ai-ppt/evaluate_presentation` with the **pre-edit version** as baseline to obtain a deterministic quality diff:
   - Pass `baseline_filepath=<pre-edit pptx path>` (the file preserved by step 5's `output_path` mechanism) alongside the current edited `filepath`. This enables the server to return `baseline_comparison` with `overall_delta` and `degraded_aspects`.
   - **baseline_comparison available** (preferred path): Read `baseline_comparison.overall_delta`. If `overall_delta < -0.3`, the edit **degraded** the presentation — **auto-revert**: restore the pre-edit version as the current file and log: `⚠️ baseline_comparison.overall_delta=<X> < -0.3 — edit degraded quality. Auto-reverting to pre-edit version.` Then proceed to step 7 (termination will trigger via the baseline regression rule).
   - **baseline_comparison unavailable** (fallback — LLM stochasticity mitigation): If `evaluate_presentation` does not return `baseline_comparison` (server does not support `baseline_filepath`, or field absent), mitigate LLM stochasticity by calling `evaluate_presentation` **twice** on the same edited file and averaging the per-aspect scores. Use the averaged scores for step 7 termination comparisons. If the standard deviation of `consolidated_score` across the two calls exceeds 1.0, emit a warning: `⚠️ LLM score variance high (σ=<X> > 1.0 across 2 evaluations) — score-based termination decisions may be unreliable. Consider manual review.` If `evaluate_presentation` fails on the retry call, fall back to the single-call result.
   - Log the evaluation method used: `ℹ️ Re-evaluation method: baseline_comparison (deterministic diff)` or `ℹ️ Re-evaluation method: dual-call average (LLM stochasticity mitigation)` or `ℹ️ Re-evaluation method: single-call (fallback).`
7. **Termination conditions** (exit loop when ANY of the **must-stop** rules is met):

   | 维度变化 | 类别 | 是否触发终止 |
   |---------|------|------------|
   | 已达 3 轮迭代上限 | hard cap | ✅ 必停 |
   | 无 severity ≥ warning 的 `recommended_actions` 剩余 | natural exit | ✅ 必停 |
   | `content` AND `coherence` 两个维度均较上一轮下降 | semantic regression | ✅ 必停 |
   | `consolidated_score` 较上一轮下降 >0.3 | consolidated regression | ✅ 必停 |
   | `baseline_comparison.overall_delta < -0.3`（server 返回） | baseline regression | ✅ 必停（已在 step 6 auto-revert） |
   | `content` OR `coherence` 仅其一下降 | single-dimension dip | ❌ 继续 |
   | `content`/`coherence` 持平或上升 | improving | ❌ 继续 |
   | `overall_score` 下降但 `content`/`coherence` 不降 | professionalism/layout interference | ❌ 继续（log advisory: `ℹ️ overall_score dropped due to non-semantic dimensions; continuing.`） |

   - **Hard cap preserved**: Maximum **3 iterations** is an unconditional ceiling — no rule may bypass it.
   - **Per-aspect data unavailable fallback**: If `evaluate_presentation` returns only `overall_score` without per-aspect breakdown, fall back to the v0.5.x rule (overall_score not improved for 2 consecutive rounds → stop) and log: `ℹ️ Per-aspect scores unavailable — using overall_score advisory comparison.` If `consolidated_score` is available, its regression rule (>0.3 drop) applies independently even when per-aspect breakdown is absent. If `baseline_comparison` is available, its regression rule (`overall_delta < -0.3`) takes precedence over inter-round consolidated_score comparison for detecting regression, as it uses deterministic server-side diff rather than stochastic LLM scoring.
   - **Visual spot-check gate**: After exiting the D.5 loop (regardless of termination reason), emit a mandatory user notice requesting visual verification of **at least 1 slide per distinct slide type** used in the deck. This catches rendering issues that LLM evaluation cannot detect (e.g., bullets rendered as table cells, structured_content collapsed to empty, chart axes unreadable).
     - **Per-type verification**: Group slides by their inferred type (from config YAML or `get_slide_info` metadata). For each type that has content slides (`bullets`, `chart`, `table`, `combo`, `canvas`), select one representative slide (prefer the lowest-scored slide in that type group, or the first occurrence if scores are unavailable). Emit: `⚠️ Visual spot-check required — verify at least 1 slide per type used:`
       ```
       - bullets: slide(s) [3, 5, 7] — verify slide 5 (lowest score)
       - chart: slide(s) [6, 9] — verify slide 6
       - table: slide(s) [8] — verify slide 8
       ```
       `LLM evaluation cannot detect rendering flattening or empty-body issues. Please visually verify the recommended slides before proceeding to Stage E.`
     - **Fallback**: If content-type metadata is unavailable (neither config YAML nor `get_slide_info` provides type information), emit a generic advisory: `ℹ️ Content-type metadata unavailable — consider a quick visual check of at least 1 bullet, 1 chart, and 1 table slide (if present) before Stage E.`
8. **Poster / single-slide protection**: Before calling `delete_slides`, use the slide count obtained from `get_presentation_info` in step 1 (re-queried after each edit iteration) as the source of truth. Check that remaining slide count after deletion would be ≥ 1. Skip deletion if it would remove all slides.
9. **Aspect-skip rules**: When the current generation path lacks the capability to address a specific low-scoring aspect, skip that aspect's actions instead of attempting unsupported edits.
   - **Trigger (charts)**: `low_aspects` includes `charts` AND the current generation path is the **quick path** (any of `generate_ppt_from_text`, `generate_ppt_from_topic`, `generate_ppt_from_file`).
     - Action: skip all `recommended_actions` whose target aspect is `charts`; do NOT attempt edits.
     - Log: `ℹ️ Skipping charts aspect — current quick path lacks chart generation capability. Recommendation: re-run via config-driven path with data_sources + chart layout declared in YAML.`
   - **Other aspects**: Continue normal action mapping; skip rules apply only to `charts` in this version. Do NOT generalize the skip to other aspects (design / layout / professionalism) without an explicit capability gap.
10. **Degradation**:
    - If `get_presentation_info` is unavailable: do not edit; emit review-only warning and proceed to Stage E.
    - If `evaluate_presentation` is unavailable but `get_presentation_info` is available: run a **deterministic degraded loop** instead of skipping D.5:
       1) read `get_presentation_info` and, when available, `read_quality_report`;
       2) derive rule-based actions from deterministic signals (overflow, empty-body, degenerate-shape, overlap);
       3) execute at most **1** conservative edit batch;
       4) re-read structural info and stop (no iterative LLM scoring).
    - Required warning format: `⚠️ evaluate_presentation unavailable — entering deterministic degraded_mode (single-pass).`

### Stage E: Review & Export
0. **De-AI-Fier Gate** [Gate D.0]: Execute `instructions/de-ai-fier-gate.instructions.md` at L2-Full for slide narrative text and speaker notes. **FAIL → fix before export.**
> ⚠️ **DS-CRITICAL**: DeepSeek V4 Pro 在该门禁维度的失效风险显著高于 Claude Opus。本门禁不得弱化为 skip/optional，不得因"看起来没问题"而跳过工具调用。若 MCP 不可用，必须标注 `[⚠️ DS-CRITICAL gate skipped — MCP unavailable]` 并通知用户。
   - **Trigger scope**: Agent-authored slide narrative, speaker notes, and synthesized summaries MUST go through L1-Tone (and L2-Full per the default above). Pure template-filled content (e.g., title-only slides, auto-generated section headers, untouched user-supplied text passed through verbatim) MAY skip; in that case, log: `ℹ️ De-AI-Fier skipped — slides contain only template-filled / user-verbatim content.`
1. **Pre-Delivery Audit** [Gate D.4]: Execute `instructions/pre-delivery-audit.instructions.md` — L1-Lite for qualitative presentations; L2-Standard if slides contain quantitative data/charts/results. Verify all numbers, units, and chart labels. Append audit table (for L1-Lite, a one-line confirmation suffices). **FAIL → block delivery.**
2. Check total time fit and information density.
3. Check visual consistency, readability, and figure-caption quality.
4. Export deliverables via `formatforge/convert_markdown_to_docx` for handouts or `formatforge/convert_markdown_to_latex` / Beamer source generation for LaTeX slide decks. Use `formatforge/lint_markdown` and `formatforge/validate_latex` to verify output quality before export.
5. **Skill Crystallization Check**: After delivery, execute `instructions/skill-crystallization.instructions.md` trigger detection (T1/T2/T3). If any trigger fires, propose crystallization to user. If none fires, skip silently.

## Critical Rules

- For `suggest_config` failure fallback, do not create or maintain a local/manual scaffold template inside this agent. Use server-returned `partial_config_yaml` as the single scaffold authority.

- Do not overload slides with long paragraphs.
- Do not place multiple unrelated core messages on one page.
- Every technical figure must include a clear caption/context line.
- Poster layouts must preserve natural scan paths (Z/F patterns).

See `instructions/presentation-templates.instructions.md` for detailed reference material.

