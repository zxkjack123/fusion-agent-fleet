---
description: "DSL reference, domain patterns, known limitations, and tool baseline for diagram-architect."
applyTo: "**"
revision: 1
---

# Diagram Architect Reference Material

Extracted from `.opencode/agent/diagram-architect.md` to reduce prompt token consumption.

## Domain-Specific Patterns (Nuclear Engineering)

- Neutronics process schematics
- Blanket architecture block diagrams
- Tritium fuel-cycle process flow diagrams
- Activation/transmutation pathway sketches
- Geometry cross-section concept diagrams

## Known Limitations & Workarounds

The following are known behavioral limitations of the tikz-writer DSL engine. Consult this section during all stages (B–D) to proactively avoid pitfalls.

1. **Back-edge handling in cyclic graphs**: The hierarchical layout algorithm does not natively render back-edges. Diagrams containing cycles will produce broken or missing edges. **Workaround**: (a) Remove the back-edge from the DSL and represent the return path with a dashed annotation arrow added manually; (b) use the `cycle_removal` parameter (`dfs_back` or `simple`) in `generate_diagram` to let the engine handle cycle breaking; (c) if MCP silently ignores `cycle_removal`, fall back to CLI: `diagram render --dsl <file> --cycle-removal dfs_back ...` (see CLI Fallback above and `instructions/tikz-writer-tools.instructions.md` § CLI Fallback Reference). For cyclic diagrams, also consider the dual-version comparison workflow (Stage B step 3.5) to let the user choose between cycle-removed and cycle-annotated versions.

2. **ALIGN / ABOVE positional constraints ignored**: DSL positional constraints such as `ALIGN` and `ABOVE` may be silently ignored by the layout algorithm, resulting in node placements that do not match the declared constraints. **Workaround**: For precise positional control, use `GROUP` to cluster related nodes together, or fall back to Track E (direct `.tex` coordinate editing).

3. **modify_diagram hallucination on complex instructions**: When given multi-step or ambiguous natural-language modification instructions (e.g., "rearrange all nodes into a 3-column grid and add decision branches"), `modify_diagram` frequently generates phantom nodes, drops existing nodes, or invents unlabeled connections. **Workaround**: Restrict `modify_diagram` to simple, single-intent edits (one node rename, one edge add/remove, one label change). For complex restructuring, use Track C (DSL rewrite) or Track D (topology transform) instead.

4. **Node ID reserved-name conflicts**: Node IDs such as `output`, `decision`, `input`, `start`, `end`, `node`, `edge` may collide with DSL keywords or layout engine internals, causing parse errors or silent misrouting. **Workaround**: Always prefix node IDs with a semantic qualifier (e.g., `proc_input`, `step_decision`, `data_output`). Never use bare generic names.

5. **aspect_ratio only stretches the canvas**: The `aspect_ratio` parameter adjusts the canvas bounding box but does **not** rearrange node positions. A narrow-tall chain of nodes with `aspect_ratio="16:9"` will simply have wide margins on both sides, not a reflowed layout. **Workaround**: To actually change the spatial arrangement, combine `aspect_ratio` with Track D (topology transform — serpentine/dual-column/grouped clusters) or Track E (direct `.tex` coordinate editing).

6. **MCP serpentine flow direction (experimental — regression observed)**: Serpentine 布局在 R6–R10 期间稳定，但 2026-04 dogfooding 发现 `_v0` 编译失败复现。降回实验性状态。Stage B step 2.5.1 不将 `serpentine` 列入 `LAYOUT_MODE_KNOWN`；当 serpentine 需求出现时，优先用 `standard`/`multi_column` + Track E coordinate template 实现蛇形效果。Track E MCP-seeded fine-tune 的 serpentine 路径保留作为尝试通道（不是首选）。Stage B step 3.1 Serpentine Quick Guard 保留作为轻量回归检测。

7. **Edge-through-node collision (engine-side gap)**: The layout engine's edge routing does not consider node bounding boxes — edges may pass directly through unrelated nodes, especially in dense layouts or when nodes have been manually repositioned. **Workaround**: Stage C step 3.2 (f) detects collisions from the `.tex` file and routes to Track E. Track E step 5.5 performs automated y-offset correction (max 3 iterations). When the tikz-writer engine adds collision-aware routing, step 3.2 (f) and step 5.5 can be deprecated.

8. **Label-label collision (engine-side improvement pending)**: Dense layouts or nodes with long labels may produce overlapping text regions. The geometric quality score (`assess_quality_enhanced`) does not penalize label overlap. **Workaround**: Stage C step 3.2 (g) detects label collisions from `.tex` bounding box parsing and routes to Track A (spacing increase) or Track E (coordinate adjustment). When the tikz-writer engine adds label collision auto-fix, step 3.2 (g) will serve as verification that the auto-fix succeeded, and the routing can be relaxed.
   *Engine-side R17 update (2026-04-25)*: `assess_quality_enhanced` and `assess_diagram_quality` now penalize `node_overlap_pairs` and `edge_node_collision_total` in the readability sub-score. MCP `data_payload` also exposes `readability`, `node_overlap_pairs`, `edge_node_collision_total`, `label_collision_count` as structured fields. Agent step 3.2(f)/(g) `.tex`-based detection remains the authoritative collision check; engine-side penalties serve as a secondary signal that flows through `readability_score` and `overall`.

## Tool Baseline

Expected tikz-writer tools as of rev date. Stage A step 0.5 diffs against this list.

| Category | Tools |
|----------|-------|
| Core | `generate_diagram`, `list_themes`, `validate_dsl`, `modify_diagram` |
| Quality | `assess_quality`, `assess_quality_enhanced`, `get_optimization_advice` |
| Journal | `list_journal_presets`, `get_journal_requirements`, `apply_journal_preset` |
| Template | `list_purpose_templates`, `apply_purpose_template` |
| Export | `export_high_resolution`, `doctor` |

Total: 14 tools. Additions or removals trigger a strategy review log entry in the iteration summary.

## tikz-writer API Orchestration

Use all key capabilities from `tikz-writer/*` according to stage purpose:

- Discovery & Environment:
  - `tikz-writer/doctor` — verify LaTeX/converter availability before workflow starts
  - `tikz-writer/list_themes`
  - `tikz-writer/list_purpose_templates`
  - `tikz-writer/list_journal_presets`
  - `tikz-writer/get_journal_requirements`
- Generation:
  - `tikz-writer/generate_diagram` — initial generation (supports `layout_mode`, `seed`, `aspect_ratio`, `tree_layout`, `auto_purpose`, `language`)
  - `tikz-writer/apply_purpose_template`
  - `tikz-writer/apply_journal_preset`
- Iterative Modification:
  - `tikz-writer/modify_diagram` — NL-driven incremental modification (preserves DSL state, avoids full regeneration)
- Validation & Quality:
  - `tikz-writer/validate_dsl`
  - `tikz-writer/assess_quality`
  - `tikz-writer/assess_quality_enhanced`
  - `tikz-writer/get_optimization_advice`
- Final Export:
  - `tikz-writer/export_high_resolution` — presets: `screen`(96)/`web`(150)/`print`(300)/`ieee`(600)/`professional`(1200)

## Quality Criteria

Evaluate each output with both metrics and visual checks:

- **Layout quality**: overlap, edge crossings, spacing, alignment, visual balance.
- **Readability**: font size, label clarity, contrast, dense-region legibility.
- **Semantic completeness**: all required components from user intent are present.
- **Style consistency**: colors, line weights, arrow styles, typography consistency.
- **Venue compliance**: size, format, and style aligned to journal/report/patent constraints.
- **Topological flow consistency**: directed edges flow in the expected direction (top-to-bottom, left-to-right, or serpentine). High geometry scores do NOT guarantee correct flow direction.
- **Sufficiency criterion** (used by MCP Sufficiency Gate and Track E engine verification): three-path OR — **Path 1 (collision-free sufficiency)**: `collision_warning_detected == false AND label_collision_free` (used by MCP Sufficiency Gate; not applied to Track E engine verification, which uses Path 2/3 only); **Path 2 (primary)**: `overall ≥ 0.80 AND label_collisions ≤ 2 AND no_truncation`; **Path 3 (backward-compatible)**: `readability ≥ 0.40 AND label_collisions ≤ 2` (relaxed from 0.45 per 2026-04 dogfooding; replaces legacy `readability ≥ 0.7` threshold which was too strict for engineering diagrams ≥10 nodes). Production verification (2026-04-23): a case with `overall=0.85` and `label_collisions=1` was accepted by this gate without forcing Track E. Note: Track E engine verification (step 7c) retains the stricter 0.45 readability threshold to avoid prematurely abandoning a converged Track E baseline.

## Critical Rules

- **ALWAYS include PNG generation for visual review, resize to a max-2000px preview copy, then inspect with `view_image`.**
- **ALWAYS run at least one quality pass using `tikz-writer/assess_quality_enhanced`.**
- **NEVER declare completion without at least one preview-based `view_image` inspection (after resize).**
- **DO NOT fabricate technical content that is not provided or inferable from user input.**
- **DO NOT replace Data Analyst’s data-driven statistical plotting scope.**
- **ALWAYS keep editable sources (DSL/TEX) in deliverables.**
- **ALWAYS maintain `current_dsl` state across iterations.** After each `generate_diagram` or `modify_diagram` call, extract and store the returned DSL for use in subsequent calls.
- **PREFER `modify_diagram` over manual DSL editing** for local changes (node add/remove/relabel, edge changes). Resort to manual DSL rewrite only for structural overhaul.
- **Seed exploration is tiered**: quality score < 0.7 → try at least 3 different seeds; quality score 0.7–0.85 AND `view_image` shows layout problems → try at least 2 different seeds; quality score unavailable AND visual issues present → treat as < 0.7. Always try seeds 7, 123, 999 before concluding layout cannot improve. Seeds with `Δoverall < 0.005 AND Δreadability < 0.005` do NOT count as exploration; after 2 consecutive no-op seeds, switch to `layout_mode` exploration (standard ↔ compact), then route to Track D if both modes exhausted. `layout_mode` switches must satisfy monotonicity: `Δoverall < -0.05` triggers immediate rollback to the previous layout_mode baseline (regenerate if no cache).
- **RUN `doctor` at Stage A** to catch environment issues early rather than discovering them at export time.
- **ALWAYS run Structural Post-Validation (step 4.5)** after every Track execution. Never skip validation even if visual preview looks acceptable.
- **`validate_dsl` is mandatory** before every `generate_diagram` (when DSL is present) and after every `modify_diagram` returns DSL. Parser errors block; warnings are logged.

## Constraints

- If tikz-writer MCP is unavailable, explicitly report the limitation and stop rather than bypassing MCP internals.
- `view_image` is a OpenCode built-in visual inspection capability (not a tikz-writer MCP API); use it for iterative review.
- If `image-worker/*` is unavailable, use a local Pillow `thumbnail((2000, 2000))` fallback to produce the preview copy before `view_image`.
- Output language follows user request (default bilingual labels when ambiguity exists).

al quality score**: X / 100 (from assess_quality_enhanced)

### Artifacts
| Format | Path | Resolution |
|--------|------|-----------|
| PNG | <path> | 300 DPI |
| PDF | <path> | vector |
| TEX (DSL) | <path> | — |

### Quality Metrics
- Node count: N / target N
- Edge crossings: N
- Label collisions: N
- Cycle handling: removed | annotated | n/a

### Pitfalls / Warnings
- <e.g., "label length > 22 chars on 3 nodes, abbreviation suggested">
- <e.g., "layout_mode degraded from serpentine → compact (auto-fold engaged)">

### Skipped / Deferred
- <iteration budget exhausted before reaching target quality>
```

### Stage B: Initial Generation

1. Build initial DSL or natural-language spec.
1.5. **Label length soft cap**: For each node label longer than 22 characters, append a DSL comment hint on the same line: `// hint: consider abbreviation (e.g., assess_quality_enhanced → assess)`. Do NOT auto-rewrite labels — let the user decide. Long labels are a leading cause of label-label collisions detected at Stage C step 3.2(g); flagging them at DSL build time enables proactive avoidance.
2. **ALWAYS run `tikz-writer/validate_dsl` on the DSL before `generate_diagram`.** If the spec is natural-language only (no DSL yet), skip this step and let `generate_diagram` produce the initial DSL, then run `validate_dsl` on the returned DSL before any subsequent `modify_diagram` or regeneration. Treat parser errors as blocking; warnings are recorded in `iteration_log` and proceed.
2.5. Select layout parameters based on diagram characteristics:

   **Layout decision matrix** (apply BEFORE the per-trait rules below; if matched, skip the same-trait per-trait rule):

   | Node count | Topology trait                     | Recommended `layout_mode`   | Rationale |
   |-----------:|------------------------------------|-----------------------------|-----------|
   |        ≤8 | any                                | `standard`                  | 引擎默认布局已足够 |
   |       9–14 | linear chain (single path)         | `serpentine`                | 折叠避免窄长形 |
   |      ≥10  | fan-in/out (multi-branch merge)    | `multi_column` / `standard` | serpentine 在多分支汇聚时易乱（r1/r2 验证） |
   |        ≥8 | branch_column (multi-branch merge)  | `branch_column`              | 多分支列布局减小宽度 |
   |       ≥15 | dense connectivity                 | `compact`                   | 节省画布 |

   决策表与下方 per-trait 规则按顺序优先匹配；若决策表命中则跳过同名 trait 规则。Topology 判定来源：从 DSL EDGE 行解析（linear chain = 每节点入度/出度 ≤1 的连通路径；fan-in/out = 任一节点入度或出度 ≥2 即视为多分支汇聚；dense = 平均度 ≥3）。若 DSL 解析失败，退回默认 `standard` + `seed=42` 并记录降级提示。

   - **≥15 nodes or dense connectivity**: `layout_mode="compact"`
   - **Tree structure (single root, acyclic)**: `tree_layout="tidy"`
   - **Slides / wide-format target**: `aspect_ratio="16:9"` + `aspect_mode="fit"`
   - **Single-column paper**: `aspect_ratio="1:1.2"` or leave unset
   - **Chinese content**: `language="zh"`
   - **First generation**: consider `auto_purpose=true` to let the engine infer a diagram type template
   - Always set `seed` (default 42) to enable reproducible layouts and later seed exploration
2.5.1. **layout_mode enum guard**: After selecting `layout_mode`, validate against the known-supported set: `LAYOUT_MODE_KNOWN = ["standard", "compact", "multi_column"]`. If the chosen value is **not** in this set:
   - Log: `"⚠️ layout_mode=<value> not in known-supported set {standard, compact, multi_column} — attempting MCP anyway. If rejected, will auto-degrade to compact."`
   - Continue to step 3 and invoke MCP with the originally chosen value (do NOT block). Subsequent post-call validation (Stage C MCP parameter verification) will detect rejection and trigger auto-degradation.
   - Rationale: the engine may have added support for new values ahead of this enum list. Warning preserves forward compatibility.
   - **Serpentine note**: The engine now includes an *auto-fold* mechanism (since layout improvements S1/S2): when `layout_mode` is `standard` or `compact`, the output is single-column, and N≥7, the engine automatically folds into a serpentine layout. This means serpentine no longer requires Track E as the primary path. However, auto-fold is a *post-processing* step on `standard`/`compact` modes — it does NOT make `layout_mode="serpentine"` itself more reliable. When the user explicitly requests `serpentine` and the explicit serpentine block fails (overlap rollback), auto-fold does NOT retry (by design — see layout.py:L311 comment). In that case, Track E remains the fallback. Summary: prefer `standard` or `auto` and let auto-fold handle folding; explicit `serpentine` is a secondary option.
3. Generate the first candidate with `tikz-writer/generate_diagram` (or `tikz-writer/apply_purpose_template` / `tikz-writer/apply_journal_preset`).
3.1. **Serpentine Quick Guard** (when serpentine/Z-shape layout was requested or implied):
   After `generate_diagram` returns, verify: (a) `tex_file` field is non-empty and the `.tex` file exists; (b) content nodes span ≥ 2 distinct y-coordinate values (indicating multi-row layout). If either check fails:
   - Log: "Serpentine output degraded — retrying with compact layout."
   - Re-generate: `generate_diagram(content=<current_dsl>, layout_mode="compact", seed=<seed>, ...)`.
   - Continue to step 4 with the compact output. Do NOT auto-set `needs_track_e`; let Stage C quality checks decide the appropriate Track.
   If passed: continue to step 3.5 / step 4.
3.5. **Cycle Detection & Dual-Version Generation** (only when DSL contains cycles):
   a. **Detect cycles**: After initial generation, check the DSL for cyclic edges (A→B→...→A paths). If `validate_dsl` reports cycle warnings, or manual inspection of EDGE declarations reveals a back-edge, set `has_cycle = true`. If no cycle exists, skip this sub-flow entirely.
   b. **Version A — Cycle-removed (clean layout)**: Generate with `cycle_removal="dfs_back"`:
      ```
      tikz-writer/generate_diagram(content=<current_dsl>, cycle_removal="dfs_back", seed=<seed>, ...)
      ```
      If MCP silently ignores `cycle_removal` (verify by inspecting `.tex` output), fall back to CLI (see CLI Fallback in Stage C).
   b2. **Validate Version A output**:
      i. Verify `tex_file` in response is non-empty and the `.tex` file exists. If missing → set `versionA_valid = false`.
      ii. Count content nodes in `.tex` (exclude `virt`/`phantom`/`dummy`-prefixed IDs and empty-label `{}` nodes). Compare against DSL NODE count. If deviation > 20% → set `versionA_valid = false`.
      iii. Count edges (`\draw`/`\path` with arrow markers) in `.tex`. Compare against DSL EDGE count. Allow ±2 for `cycle_removal` edge changes. If deviation beyond ±2 AND > 30% → set `versionA_valid = false`.
      iv. If any check fails: log `"Cycle Version A validation failed: [detail]"`.
   c. **Version B — Cycle-annotated (complete information)**: Generate with `cycle_removal="none"`:
      ```
      tikz-writer/generate_diagram(content=<current_dsl>, cycle_removal="none", seed=<seed>, ...)
      ```
      If the layout engine produces broken edges for the cycle, manually add dashed arc back-edges in the `.tex` file (Track E technique).
   c2. **Validate Version B output** (same checks as b2, using `versionB_valid`):
      i. Verify `tex_file` exists. If missing → set `versionB_valid = false`.
      ii. Count content nodes (exclude virt/phantom/dummy + empty labels). Deviation > 20% from DSL NODE count → set `versionB_valid = false`.
      iii. Count edges. Allow ±2 for cycle handling. Deviation beyond ±2 AND > 30% → set `versionB_valid = false`.
      iv. If any check fails: log `"Cycle Version B validation failed: [detail]"`.
   c3. **Cycle validation fallback**:
      - If `versionA_valid = false` AND `versionB_valid = false`: Log `"Both cycle graph versions failed validation — falling back to compact + Track E."` Re-generate: `generate_diagram(content=<current_dsl>, layout_mode="compact", seed=<seed>)`. Set `needs_track_e = true`. Skip to step 4.
      - If only one version valid: proceed to (d) with the valid version only; skip user comparison (auto-select the valid version).
      - If both valid: proceed to (d)/(e)/(f) normally.
   d. **Preview both**: Create max-2000px previews for both versions → `view_image` each.
   e. **Present comparison**: Show both versions to the user with a recommendation:
      - Recommend Version A if the cycle-removed layout is significantly cleaner and the back-edge information can be conveyed in a caption or legend.
      - Recommend Version B if the cycle is semantically critical (e.g., feedback loops in control systems, iterative processes).
   f. **User selects**: Set the chosen version's DSL as `current_dsl` for Stage C iteration. Only the selected version proceeds — dual-version generation occurs only at this initial stage, not in subsequent iteration rounds.
4. Ensure PNG output exists; run `image-worker/resize_image` to create a preview copy (e.g., `<output>_preview.png`, max 2000×2000 via `fit='inside'`, `withoutEnlargement=true`), then inspect the preview with `view_image`.
5. Record initial visual findings (readability, overlap, spacing, hierarchy, completeness).

### Stage C: Quality Assessment & Iteration (Core Loop)

**DSL State Rule**: Maintain a `current_dsl` variable across iterations. Update it after every `generate_diagram` or `modify_diagram` call with the returned DSL.

**Iteration Log Structure** (maintained throughout Stage C):

Append one entry per `generate_diagram` / `modify_diagram` call. Schema:
```
{
  round:              <int, 1-based>,
  track:              <"A"|"B"|"C"|"D"|"E">,
  seed:               <int|null>,
  layout_mode:        <"standard"|"compact"|"serpentine"|...|null>,
  overall:            <float|null>,        // from assess_quality_enhanced
  readability:        <float|null>,        // from assess_quality_enhanced or estimated
  label_collisions:   <int|null>,          // from step 3.2(g); when collision_counts available, = collision_counts.label_collision_count + collision_counts.label_edge_collision_count
  delta_overall:      <float|null>,        // overall - prev.overall (null on round 1)
  delta_readability:  <float|null>,        // readability - prev.readability
  action:             <"accept"|"reseed"|"layout_switch"|"track_switch"|"stop"|"fast-pass"|"unreachable"|"seed-invariant"|"layout_mode_inert">,
  notes:              <free-form string, e.g., "Δ < 0.005, switch to compact">,
  warnings:           <list[str]|null>,  // all MCP warnings from generate_diagram data.warnings + assess_quality_enhanced QA warnings + Channel A pseudo-warnings this round; empty list [] = MCP returned warnings array with zero entries; null = warnings field not present in MCP response
  collision_counts:   <{node_overlap_pairs: int, edge_node_collision_total: int, label_collision_count: int, label_edge_collision_count: int}|null>  // from assess_quality_enhanced data_payload; null if unavailable (STALE mode, image-only, old engine)
}
```
Read by: Track B Δ early-stop check (Task 1.2), Stop Conditions fast-pass (Task 2.2), Unreachable Declaration trigger (Task 3.2), Phase 1 dual-candidate comparison (Task 3.1).
Persistence: in-session only (no file I/O); reset between user requests. If append fails (state corruption), degrade to current-round-only logging and continue main flow.

**Step 0: Dual-Candidate Pre-Loop** (runs once before the main iteration loop; does NOT consume the 5-round budget):
When the DSL has ≥ 9 nodes AND `layout_mode` is not explicitly set by the user:
  a-pre. **Topology pre-filter (Pre-Loop skip heuristic)**:
     Parse DSL EDGE declarations on the raw graph (before any cycle removal). Compute:
     - `max_in_degree`: max number of incoming edges for any node
     - `max_out_degree`: max number of outgoing edges for any node
     - `has_cycle`: true if `validate_dsl` reported a cycle warning
     - `satellite_count`: count of nodes with in_degree==0 AND out_degree==1 AND whose sole target has in_degree>=2 (satellite feeders, not the graph's primary source)
     If ALL of: `has_cycle == true AND max_in_degree <= 2 AND max_out_degree <= 2 AND N >= 8 AND satellite_count <= 2`:
     → This is a "linear chain + back-edge" topology. `standard` and `compact` produce identical single-column output (`layout_mode_inert`). Skip Pre-Loop.
     Log: `"Pre-Loop topology pre-filter: linear chain + cycle (N={N}, max_in={max_in_degree}, max_out={max_out_degree}, satellites={satellite_count}). Skipping dual-candidate generation."`
     Set `layout_mode_inert = true`. Adopt `standard` + seed=42 as baseline. Proceed to main iteration loop.
     If ANY condition fails: proceed to sub-step a-pre-2.
  a-pre-2. **Composite topology fast-path** (satellite + cycle → Track E):
     If ALL of: `has_cycle == true AND satellite_count >= 3 AND N >= 9`:
     → This topology combines feedback loops with satellite feeders, which causes the orth router to produce crossing paths and endpoint routing anomalies. Track A/B iteration cannot fix engine-level routing issues.
     Set `needs_track_e = true`. Set `layout_mode_inert = true`.
     Log: `"Composite topology detected (cycle + satellite, N={N}, satellites={satellite_count}). Fast-path to Track E. (dual-candidate skipped — layout_mode_inert expected)"`
     Skip Step 0 dual-candidate generation entirely. Proceed to main loop step 3 with `needs_track_e` flag (Decision Gate will route to Track E on first round).
     If ANY condition fails: proceed to sub-step (a) as before (run full Pre-Loop).
  a. Generate candidate A: `generate_diagram(content=<current_dsl>, layout_mode="standard", seed=42, ...)`. Run `assess_quality_enhanced` on candidate A. Record as `iteration_log` entry with `round: "0a"`.
  b. Generate candidate B: `generate_diagram(content=<current_dsl>, layout_mode="compact", seed=42, ...)`. Run `assess_quality_enhanced` on candidate B. Record as `iteration_log` entry with `round: "0b"`.
  b-bis. **Identity check (B4)** — pixel-level equality detection between candidates A and B:
     Performed only when both candidates A and B produced PNG output (path available in `generate_diagram` response). Three-level cascade — short-circuit on first failure:
     1. **File size**: compare `os.path.getsize(png_A)` vs `os.path.getsize(png_B)` (Task Executor may use `bash stat -c %s` or equivalent). If sizes differ by ≥ 1 byte, candidates are NOT identical → skip remaining levels, proceed to (c).
     2. **PNG dimensions**: read the IHDR chunk from each PNG (bytes 16–23 of file: width and height as big-endian uint32; Task Executor may use `xxd -p -s 16 -l 8 <png>` or `python3 -c "import struct; print(struct.unpack('>II', open(p,'rb').read(24)[16:24]))"`). If width or height differ, NOT identical → skip level 3, proceed to (c).
     3. **md5 hash**: compute `md5sum png_A` and `md5sum png_B`. If hashes equal, candidates are pixel-identical. If `md5sum` is unavailable on the system, log `"identity check partial — md5 skipped, relying on size+dimensions only"` and treat size+dimensions match as identity.
     If all available levels confirm identity (or md5 was skipped due to tool absence and size+dimensions matched):
     - Set session flag `layout_mode_inert = true`.
     - Log: `"Step 0 identity check: candidates A (standard) and B (compact) are pixel-identical (size={S}, dim={W}x{H}, md5={hash_or_skipped}). DSL is layout_mode-inert; setting layout_mode_inert=true and short-circuiting pre-loop."`
     - Record an `iteration_log` entry with `round="0b-bis"`, `action="layout_mode_inert"`, `notes="pre-loop identity check confirmed inert"`.
     - Skip sub-step (d) selection heuristic entirely.
     - Adopt candidate A (standard) as the winner per sub-step (e), since standard is the more predictable mode (consistent with current second tie-break rule).
     - Proceed to the main iteration loop. Track B will short-circuit at its top via the **layout_mode_inert short-circuit guard** (set by Task 1.1) and route directly to Track E without any further layout_mode/seed exploration.
     If identity is NOT confirmed (any level differs, or PNG paths unavailable, or file read fails): proceed to sub-step (c) → (d) as before. Log `"Step 0 identity check: candidates differ at level {N} ({reason}); proceeding with weighted_score selection"` (or `"Step 0 identity check skipped: PNG path unavailable for candidate {A|B}; proceeding with weighted_score selection"`).
  c. If either candidate generation fails (MCP error/timeout), adopt the successful one. If both fail, fall back to the existing single-candidate path (step 1 onward with default layout_mode).
  d. **Selection heuristic**: Read structured collision counts from each candidate's `assess_quality_enhanced` `data_payload`:
     - `collision_score = (node_overlap_pairs + edge_node_collision_total + label_collision_count + label_edge_collision_count) × 3`
     - `non_collision_warnings = len(data.warnings) - (number of warnings matching step 3.1.5 Channel B substrings)`
     - `weighted_score = collision_score + non_collision_warnings`
     Select the candidate with lower `weighted_score`. If `data_payload` is unavailable for either candidate, fall back to step 3.1.5 Channel B substring counting on `data.warnings` (collision-class substrings ×3, others ×1). Tie-break: higher `overall` from `assess_quality_enhanced`. Second tie-break: prefer `standard` (more predictable).
  e. Set `current_dsl` to the winner's DSL. Set `current_layout_mode` to the winner's layout_mode.
  f. The main iteration loop starts at round 1 with the winner. **Δ early-stop check**: when computing `Δoverall` in Track B, compare only against the most recent `iteration_log` entry with the SAME `layout_mode` value (skip entries from a different mode, including the pre-loop loser). This prevents apples-to-oranges Δ comparisons across modes.
When the DSL has < 9 nodes OR `layout_mode` is explicitly set: skip Step 0 entirely.

For each iteration round (max 5 rounds): (Pre-loop candidates from Step 0, if any, do not count toward this budget.)

1. Run `tikz-writer/assess_quality_enhanced` for quantitative indicators.
   - **`diagram_path` usage**: Always pass `diagram_path=<latest_png_or_pdf_path>` alongside `dsl_content` for combined DSL + image-level quality assessment.
   - **STALE mode (after Track E)**: When `current_dsl` is STALE, DSL-based quality assessment is unavailable. Pass `diagram_path=<compiled_png_or_pdf>` to `assess_quality_enhanced` (without `dsl_content`) for image-level quality metrics. Supplement with `view_image` visual judgment.
     - **Shadow DSL structural check (A2)**: In STALE mode, also invoke `skills/tikz-track-e/scripts/extract_shadow_dsl.py` against the latest `.tex` to reconstruct a `{nodes, edges}` snapshot. Use it to verify node count, edge count, and the node-id set against the pre-Track-E DSL. Treat divergence (missing nodes, dropped edges) as a Track E regression and revert before re-evaluating quality.
     - **Post-compile AABB collision check (A3)**: After every successful Track E recompile, before `view_image`, invoke `skills/tikz-track-e/scripts/aabb_check.py` on the compiled `.tex`. A non-empty `edge_through_node` list is a hard Track E failure — revert the edit, refine the `track_e_ops` call (different waypoints, alternate routing), and recompile. A non-empty `node_collisions` list demotes the round to retry rather than accept. Note: AABB uses `node_size_default=(1.8, 0.6)` and has ~20% false positives on `text width=...` nodes; treat as warning when only `node_collisions` triggers.
   - **Readability extraction**: Record the readability metric from `assess_quality_enhanced` output (field name may be `readability`, `font_legibility`, or similar). If no explicit readability metric is returned, estimate from composite indicators: low edge crossing count + adequate label-to-node spacing + `view_image` visual legibility judgment. Store as `readability_score` (0–1 scale). Current engine baseline: ~0.45 for complex layouts.
2. Run `tikz-writer/get_optimization_advice` for actionable improvements.
3. Combine `view_image` visual feedback with quality metrics.
3.1.5. **MCP Warning Pre-Filter** (collision-class warnings hard reject):
   After step 3 (assess_quality_enhanced + get_optimization_advice + view_image), apply
   two-channel detection (structured fields are primary; substring matching is fallback):

   **Channel A — structured fields (primary)**: If `assess_quality_enhanced` has been
   run this round and returned `data_payload`, check:
     `node_overlap_pairs > 0 OR edge_node_collision_total > 0 OR label_collision_count > 0 OR label_edge_collision_count > 0`
   If ANY condition is true, set `collision_warning_detected = true`.
   Synthesize a pseudo-warning for iteration_log: `"[structured] data_payload: node_overlap_pairs={N}, edge_node_collision_total={M}, label_collision_count={K}, label_edge_collision_count={L}"`
   and log: `"MCP collision warning pre-filter (Channel A) triggered: {pseudo_warning}"`.
   If `data_payload` is absent or the fields are missing (older tikz-writer version,
   image-only mode, STALE mode), log `"structured collision data unavailable — falling
   back to Channel B substring matching"` and mark Channel A as unavailable.

   **Channel B — substring matching (fallback)**: Activated only when Channel A is
   unavailable. Scan the MCP response `warnings` array (collected from `generate_diagram`
   and/or `assess_quality_enhanced` outputs of the latest round). If ANY warning string
   contains one of the following substrings (case-insensitive):
     - `"node overlap"`
     - `"edge-node collision"`
     - `"label-edge collision"`
     - `"label-node overlap"`
     - `"label overlap"`
   then set `collision_warning_detected = true` and record the matched substring.
   Log: `"MCP collision warning pre-filter (Channel B) triggered: {matched_warning}"`.

   **Combined result**: `collision_warning_detected = (Channel A) OR (Channel A unavailable AND Channel B)`.
   This fires BEFORE step 3.2(f)/(g) `.tex` parsing, providing an early-exit for
   "high-score disaster" scenarios where `overall` is high but visual collisions exist.
   The flag is consumed by Decision Gate **Hard overrides** (step 4) to force routing
   into Track B/D/E (skipping Track A — `modify_diagram` cannot fix engine-side
   collisions). Step 3.2(f)/(g) still run for downstream diagnostics, but the routing
   decision is already locked.
   If NEITHER channel matches: set `collision_warning_detected = false` and continue
   normally to step 3.2.
3.1.6. **Auto-Fold Fast-Pass** (skip iteration when auto-fold produced a clean result):
   When the `generate_diagram` response meta indicates `auto_fold_applied == true` (the engine's auto-fold activated and reshaped the layout), check ALL of:
   - `collision_warning_detected == false` (from step 3.1.5)
   - `label_collision_free == true` (from step 3.2(g), or if not yet computed, perform the label collision check from step 3.2(g) now)
   - `assess_quality_enhanced` returned `image_quality.aspect_ratio` ∈ [0.5, 3.0]
   If ALL conditions pass: set `mcp_sufficiency_passed = true`. Log: `"Auto-fold fast-pass: auto_fold_applied + collision_free + aspect normal ({aspect_ratio}). Skipping iteration."`. Skip the remainder of step 3.2 and step 4 (Decision Gate), proceed directly to finalization (step 5/6).
   If ANY condition fails: continue normally to step 3.2 (no fast-pass).
3.2. **Topological Flow Consistency Check** (for flowcharts, process flows, and sequential diagrams only — skip for concept maps, undirected graphs, and free-form schematics):
   `assess_quality_enhanced` scores geometry (spacing, overlap, symmetry) but does NOT validate edge direction semantics. A diagram can score > 0.85 while having reversed flow directions. Perform this check after step 3:
   a. Determine the expected primary flow direction from the diagram type:
      - Top-to-bottom: B.y ≤ A.y for each edge A→B
      - Left-to-right: B.x ≥ A.x for each edge A→B
      - Serpentine: even rows (0-indexed) L→R (B.x > A.x), odd rows R→L (B.x < A.x); row transitions: B.y < A.y (downward)
   b. Extract node coordinates from `.tex` (parse `\node... at (x, y)`) or from `view_image` visual inspection. If `.tex` is unavailable or `current_dsl` is STALE with no compiled `.tex`, use `view_image` visual judgment as fallback.
   b-bis. **Back-edge exemption** (active only when most recent `generate_diagram` call used `cycle_removal="dfs_back"`):
      - Run DFS on DSL EDGE list, treating the first declared source node (or any node with in-degree 0; if none, the first declared node) as the root.
      - Mark an edge A→B as a `back_edge` if B is an ancestor of A in the current DFS stack (classical DFS back-edge definition).
      - Build set `BACK_EDGES = {(A,B): edge is back-edge}`. If DSL has no cycles, `BACK_EDGES = ∅` and this sub-step is a no-op.
      - In sub-step (c) below, skip back-edges in BOTH `violations` and `total_directed_edges` counts (i.e., they are excluded from the denominator and the numerator). Log: `"Excluded {N} back-edges from flow check (cycle_removal=dfs_back)"`.
      If `cycle_removal` was not `"dfs_back"` for the most recent generation, skip this sub-step entirely; sub-step (c) operates on all edges as before.
   c. For each directed edge A→B (excluding edges in BACK_EDGES per sub-step (b-bis)), check if B is in the expected direction from A. Count violations. Compute `violation_ratio = violations / total_directed_edges` (where `total_directed_edges` also excludes BACK_EDGES).
   d. If `violation_ratio > 0.2` OR `violations ≥ 3`:
      - Set `topo_flow_violation = true`.
      - Log: "Topological flow violation detected: {violations}/{total} edges reversed."
      - This finding OVERRIDES a high `assess_quality_enhanced` score — route to Track E (edge routing fix) or Track D (topology transform), even if score > 0.85.
   e. If no violation: continue normally to step 3.5.
   f. **Edge-through-node collision check** (all tracks, all diagram types):
      Edges routed by the layout engine may pass through unrelated nodes. This check detects such collisions:
      i. Parse all `\node` declarations from `.tex` to build a node bounding-box map: for each node, extract center `(x, y)` from `at (x, y)`, and dimensions from `minimum width`/`minimum height` in the node style (default fallback: 1.5cm × 0.8cm). Compute bounding box as `[x - w/2, x + w/2] × [y - h/2, y + h/2]`.
      ii. Parse all `\draw`/`\path` commands. For each edge from source to target, extract the polyline segments (expand TikZ coordinate expressions like `-- ++(dx,dy)`, `(nodeA |- nodeB)`, control point coordinates). Approximate bezier curves as polylines through their control points.
      iii. For each polyline segment of each edge, check if it intersects the bounding box of any node that is NOT the source or target of that edge (AABB line-segment intersection test).
      iii-bis. **Endpoint routing anomaly — structured field shortcut** (forward-looking, conditional): If `assess_quality_enhanced` returned `data_payload` with field `endpoint_routing_anomaly` AND `endpoint_routing_anomaly > 0`: set `endpoint_anomaly = true`, then evaluate the **Multi-column fallback** defined in iii-ter below before propagating to `edge_collision = true`. Log `"Endpoint routing anomaly detected via structured field (endpoint_routing_anomaly={N})"`. **Multi-column fallback applies here too**: if the structured field fires under `layout_mode="multi_column"`, follow the same fallback rule defined in iii-ter below before setting `edge_collision = true`. If the field is absent from `data_payload`: silently proceed to iii-ter (no log, no degradation — this field is forward-looking and not yet available in all tikz-writer versions).
      iii-ter. **Endpoint direction monotonicity check** (`.tex` level, runs only when step 3.2(a) determined a flow direction; skip for concept maps / undirected graphs): For each `\draw`/`\path` edge, extract the first 2 coordinate points (departure segment) and last 2 coordinate points (arrival segment) from the path:
         - For `--` straight segments: read explicit `(x1,y1) -- (x2,y2)` coordinates.
         - For `to[out=α, in=β]` curved segments: use `out` angle for departure direction, `in` angle for arrival direction (angle 0=right, 90=up, 180=left, 270=down).
         - For bezier `.. controls (cx,cy) ..`: use direction from source to first control point as departure, last control point to target as arrival.
         Check departure/arrival direction against expected flow direction (from step 3.2(a)):
         - Top-to-bottom: departure Δy ≤ 0 (down or level), arrival Δy ≤ 0.
         - Left-to-right: departure Δx ≥ 0 (right or level), arrival Δx ≥ 0.
         - Serpentine: follow row-specific direction per step 3.2(a).
         If ANY edge's departure OR arrival direction violates the expected flow: set `endpoint_anomaly = true`, log `"Endpoint direction anomaly: edge {src}→{tgt} departs/arrives against {flow_direction} flow"`.
         **Multi-column fallback** (B4): Before propagating `endpoint_anomaly = true` to `edge_collision = true`, check the current `layout_mode`:
         - If `layout_mode == "multi_column"` AND `standard` mode has NOT yet been tried in the current iteration (consult `iteration_log` for entries with `layout_mode == "standard"`): Before forcing the switch to standard, check `layout_mode_inert`; if true, skip the forced switch and proceed with `edge_collision = true` immediately (route to Track E per the existing hard override). Otherwise, do NOT set `edge_collision = true` yet. Instead, route to **Track B layout_mode exploration** with a forced switch to `standard` (treat this as an endpoint-anomaly-driven switch, bypassing Δ early-stop). Re-evaluate step 3.2(f) i–iii-ter on the new output.
         - If `layout_mode == "multi_column"` AND `standard` was already tried this iteration with the anomaly persisting, OR `layout_mode != "multi_column"`: proceed with `edge_collision = true` as before.
         - Note: this fallback does NOT apply to sub-step (iii) edge-through-node AABB collisions — those are true geometric intersections, not column-order artifacts. The multi_column fallback only intercepts `endpoint_anomaly` from iii-ter (and from iii-bis when the structured field fires).
         After scanning all edges: if `endpoint_anomaly == true` and the Multi-column fallback above did not intercept, set `edge_collision = true` (reuses the existing Track E hard-override route — no new Decision Gate override). If `.tex` is unavailable or path coordinates cannot be parsed (e.g., `\foreach` macros, unexpanded TikZ macros): skip this edge and log `"Endpoint monotonicity check skipped — coordinates unparseable"`.
      iv. If any collision is detected: set `edge_collision = true`, log `"Edge {src}→{tgt} collides with node {collider}"`. Route to Track E for edge re-routing (Track E step 5.5 will handle the fix). This includes edge-through-node collisions (iii), endpoint routing anomalies (iii-bis), and endpoint direction violations (iii-ter). **Hard override**: `edge_collision == true` is a HARD trigger for Track E — do NOT attempt Track A (`modify_diagram` cannot fix engine-side edge routing), Track B (reseeding rarely improves edge collisions in fan-in/out topologies), or Track D (topology transform changes node positions but the engine still routes edges through unrelated nodes). Skip Decision Gate's normal A→B→D priority.
      v. If `.tex` is unavailable (no compiled output): skip this check with log `"Edge collision check skipped — .tex unavailable, relying on visual inspection"`, and rely on `view_image` visual judgment as fallback.
      vi. If no collision: continue normally to step 3.2 (g).
   g. **Label collision check (node-node + edge-label-node)** (all tracks, all diagram types):
      Dense layouts or long-label nodes may produce overlapping text regions that the geometric quality score does not penalize. Edge labels (`node[midway]{...}` markers) may also overlap unrelated node labels. This check verifies label separation across both node-node and edge-label-vs-node pairs:

      **Structured field shortcut** (preferred when available): If `assess_quality_enhanced` returned `data_payload` with `label_collision_count` and `label_edge_collision_count` this round, consume them directly:
      - If `label_edge_collision_count > 0`: set `label_collision = true`. Log: `"Edge-label collision detected via structured field (label_edge_collision_count={N})"`. Route DIRECTLY to **Track E** — `modify_diagram` cannot reposition edge labels.
      - Else if `label_collision_count > 0`: set `label_collision = true`. Log: `"Label collision detected via structured field (label_collision_count={N})"`. Route to **Track A** first (spacing adjustment); if Track A fails after 1 attempt, route to Track E.
      - Else (both == 0): set `label_collision_free = true`. Skip .tex parsing, continue to step 3.5.
      If `data_payload` is unavailable (STALE mode, image-only mode, old engine version): fall back to .tex parsing below.

      **.tex parsing fallback** (when structured fields unavailable):
      i. Parse all `\node` declarations from `.tex`. For each node, extract center `(x, y)`, label text, and node dimensions (`minimum width`/`minimum height` from style; if unspecified, estimate width = max(label_character_count × 0.25cm, 1.5cm), height = 0.8cm).
      i-bis. Parse edge label declarations from `.tex`. Edge labels appear as:
         - `node[midway, above]{<label>}` / `node[midway]{<label>}` / `node[pos=0.5]{<label>}` inline in `\draw`/`\path` commands
         - `\path (src) -- node {<label>} (tgt)` standalone label nodes
         For each edge label, estimate center position as the midpoint of source and target node coordinates (or from explicit `at (x,y)` if present). Estimate dimensions = max(label_char_count × 0.25cm, 1.0cm) × 0.6cm (edge labels are typically smaller than node labels). Compute edge-label bounding box with 0.1cm padding. Skip empty `{}` edge labels.
      ii. Compute label bounding box: `[x - w/2 - 0.15, x + w/2 + 0.15] × [y - h/2 - 0.1, y + h/2 + 0.1]` (0.15cm horizontal / 0.1cm vertical font padding) for node labels; for edge labels use the smaller padding (0.1cm) defined above.
      iii. Check AABB intersection across two pair categories:
         - **Node-node**: each unordered pair of nodes — compute label bbox overlap area.
         - **Edge-label vs node**: each edge label against each node label. **Proximity exemption**: for the source and target nodes of the edge, compute `proximity_ratio = Euclidean(edge_label_center, nearest_endpoint_center) / edge_straight_line_length`. If `edge_straight_line_length < 0.01` (degenerate/self-loop), set `proximity_ratio = 1.0` (no exemption). If `proximity_ratio < 0.3`, exempt this pair (label is close enough to its own endpoint to be intentionally adjacent). Otherwise, check overlap normally. For edge labels with explicit `pos=P` in the `.tex`, estimate label center as the point at fraction P along the source→target vector (instead of midpoint). Compute overlap area.
      iv. If any node-node overlap area > 0.3 cm²: set `label_collision = true`, log `"Label collision: node {A} overlaps node {B} (overlap: {area:.2f} cm²)"`. Route to Track A (`modify_diagram` with spacing increase instruction) first; if Track A cannot resolve after 1 attempt, route to Track E for direct coordinate adjustment.
         If any edge-label-vs-node overlap area > 0.3 cm²: set `label_collision = true`, log `"Edge-label collision: edge {src}→{tgt} label overlaps node {C} (overlap: {area:.2f} cm²)"`. Edge-label pairs that passed the proximity exemption (`proximity_ratio < 0.3`) are excluded from collision count. Route DIRECTLY to **Track E** (skip Track A) — `modify_diagram` cannot reposition edge labels; only `.tex`-level coordinate / `pos=` adjustment can fix this.
      v. If `.tex` is unavailable AND structured fields unavailable: skip with log `"Label collision check skipped — .tex unavailable"`, rely on `view_image` visual judgment as fallback.
      vi. If no collision: set `label_collision_free = true`, continue to step 3.5.
3.5. **CT Diagram Logic Validation (optional)**: For causal flowcharts, decision trees, or system architecture diagrams, optionally delegate to `Critical Thinking` to review diagram logic: (a) "Are causal directions correct?"; (b) "Are critical paths or feedback loops missing?"; (c) "Does the diagram narrative match the prose description?". Incorporate CT findings into the current revision round. *Fallback if CT unavailable*: self-check the three points above.
4. **Select modification strategy** based on issue type:

   **Decision Gate** — Choose the track before acting. Do NOT regenerate from scratch when `modify_diagram` can address the issue.

   **Hard overrides** (evaluated BEFORE Default → Track A):
   - If `edge_collision == true` (set by step 3.2(f)): jump directly to **Track E**, skip A/B/D entirely. Rationale: engine-side edge routing cannot be fixed by DSL-level tracks.
   - If `topo_flow_violation == true` (set by step 3.2(d)): route to **Track E** (or **Track D** for topology transform per existing rules in step 3.2(d)).
   - If `collision_warning_detected == true` (set by step 3.1.5): route to **Track B / D / E** (skip Track A — `modify_diagram` cannot fix engine-side collisions surfaced via MCP warnings). Default routing: try Track B first; if Track B already exhausted (per Δ early-stop / layout_mode monotonicity) route to Track D; if Track D also fails, route to Track E. This override fires regardless of `overall` score (a "high-score disaster" with collision warnings is still rejected).
   - If MCP response `warnings` array contains any string matching `"aspect ratio is extreme"` (substring match, case-insensitive) OR `assess_quality_enhanced` returns `aspect_ratio < 0.3` or `aspect_ratio > 3.0`: check rendered aspect — if `assess_quality_enhanced` returns `image_quality.aspect_ratio` ∈ [0.5, 3.0] (rendered aspect is normal despite the warning), log `"Extreme aspect warning present but rendered aspect ({value}) is normal — hard override suppressed."` and do NOT set `extreme_aspect`. Otherwise set `extreme_aspect = true`. Jump directly to **Track E**, skip A/B/D entirely. Rationale: extreme aspect indicates the engine's auto-fold did not activate or failed; Track B seed exploration cannot change canvas shape; Track D topology transform is a theoretical path but Track E is more direct and reliable. Log: `"Extreme aspect ratio detected ({value}) — routing to Track E (hard override)."`.
   - **extreme_aspect hard abort** (evaluated as the FIRST hard override on round ≥ 2): If `iteration_log[-1].warnings` contains `"extreme_aspect"` or `"aspect ratio is extreme"`, set `needs_track_e = true` and **skip all `generate_diagram`/`modify_diagram` calls**. Subsequent rounds are limited to Track E operations (manual .tex edit + compile + quality check) — do NOT call `generate_diagram` or `modify_diagram` again. This abort only auto-fires on rounds after the first extreme_aspect trigger. **Override clause**: If the user explicitly says "retry generate_diagram" or "try again from scratch", log `"User override: extreme_aspect abort lifted per user request."` and allow one `generate_diagram` call. Do NOT lift automatically.

   - **Default → Track A**: node-level changes (add/remove/move/relabel nodes, adjust connections). If unsure, start here. **Trivial-operation bypass**: If the requested change is ONE atomic operation — single node rename/relabel, single node move (group/align context only), or single edge add/remove — route directly to **Track C (DSL rewrite)** with a 1–2 line string replacement. Track A's `modify_diagram` has shown REJECT/hallucination even on trivial ops; Track C is more controllable for atomic changes.
   - **→ Track B**: content is correct but overall layout quality is poor (crowding, excessive edge crossings, uneven spacing). See tiered trigger thresholds.
   - **→ Track D**: content and connections are correct but diagram shape mismatches target aspect ratio (e.g., linear chain renders as narrow-tall strip).
   - **→ Track E (precision fallback for spatial control beyond engine capability)**: Route here when: (a) user explicitly requires precise coordinate control that the engine cannot produce to sufficient quality (multi-column/grid/serpentine layouts are now handled by the engine — only route to Track E if engine output fails quality checks or user demands pixel-level adjustments); (b) layout requirement matches a Known Limitations DSL-unsolvable item (e.g., #2 ALIGN/ABOVE ignored, #5 aspect_ratio canvas-only); (c) DSL-level approaches (Tracks A–D) have failed to achieve target layout after ≥ 2 attempts.
     **MCP Sufficiency Gate** (applies to triggers (a) and (b) only, when no semantic override is active): Before entering Track E, verify ALL of: (1) `topo_flow_violation` is false (step 3.2(d)); (2) `edge_collision` is false (step 3.2(f)); (3) **composite quality judgement** — three-path OR: **Path 1 (collision-free sufficiency)** — `collision_warning_detected == false AND label_collision_free` (visual zero-collision is itself sufficient regardless of `overall`); OR **Path 2 (primary)** — `overall ≥ 0.80 AND label_collisions ≤ 2 AND no_truncation`; OR **Path 3 (backward-compatible)** — `readability_score ≥ 0.40 AND label_collisions ≤ 2` (relaxed from 0.45 per 2026-04 dogfooding; use this fallback when `overall` field is missing from MCP response or when `no_truncation` cannot be determined); AND (4') **topological correctness** — `topological_correctness >= 0.85` when the field is present in the MCP response (S6/T3.2); if the field is missing (older server), skip this sub-condition and log warning `"topological_correctness unavailable — skipped (server pre-S6)"`. Field name `overall` may appear as `overall_score` / `score` depending on `assess_quality_enhanced` version — match by semantic role. `no_truncation` means no node label is clipped by node bounding box; if the metric is unavailable, fall back to `view_image` visual confirmation that no label is truncated; (4) `label_collision_free` (step 3.2(g)). If all conditions pass, the MCP output meets quality AND has no semantic issues — do NOT enter Track E; continue iteration via Track A/B. Log: "MCP Sufficiency Gate passed — Track E skipped." If ANY condition fails, proceed with Track E routing as normal. Trigger (c) bypasses this gate entirely (repeated Track A–D failure is unconditional).
     Track E uses MCP-seeded fine-tune as its primary procedure (clean virtNodes, fix edge routing, adjust spacing from MCP output), falling back to from-scratch coordinate templates only when MCP output is unusable.
   - **→ Track C**: fundamental restructuring needed — diagram type change, hierarchy overhaul, or starting over from scratch.

   **Track A — NL Patch [DEFAULT]**:
   Use when: adding/removing/moving individual nodes, relabeling, adjusting connections. **Note**: trivial single-atom operations should bypass Track A and go to Track C (see Decision Gate). Track A is preferred only for **multi-node** rearrangements within ONE modify call (e.g., `add 2 decision branches and relabel root`). For complex multi-node rearrangements beyond what one modify call can reliably handle, prefer Track C or Track D over Track A to avoid modify_diagram hallucination (see Known Limitations).
   Pre-modify: record `N_pre` = count of NODE declaration lines in `current_dsl`, `E_pre` = count of EDGE/connection declaration lines.
   ```
   tikz-writer/modify_diagram(
     modification="<natural language change description>",
     current_dsl=<current_dsl>,
     theme=<same_theme>,
     seed=<same_seed>,
     language=<same_language>
   )
   → Capture returned DSL as candidate_dsl (do NOT update current_dsl yet)
   ```
   Post-modify sanity gate (before proceeding to step 4.5):
   0. **Validate first**: Run `tikz-writer/validate_dsl(candidate_dsl)`. If validation reports errors, **REJECT immediately** (treat as Track A failure, fall back per Track A step (d) — Track B/C/E). Warnings are logged to `iteration_log` and proceed.
   a. **Count gate**: Parse `candidate_dsl`, count `N_out` (NODE lines) and `E_out` (EDGE lines). Compute `N_expected = N_pre ± explicitly requested additions/removals` (same logic for `E_expected`).
      - If `N_expected > 5` and `|N_out - N_expected| / N_expected > 0.20`: **REJECT**.
      - If `N_expected ≤ 5` and `|N_out - N_expected| > 1` (excluding explicitly requested changes): **REJECT**.
      - Edge check: if `|E_out - E_expected| / max(E_expected, 1) > 0.30`: **REJECT** (edges can diverge more due to routing).
   b. **ID integrity**: Verify `candidate_dsl` contains ALL node IDs that were present before modification (unless the modification explicitly requested removal).
   c. **No phantoms**: Verify NO new node IDs appear in `candidate_dsl` that were not explicitly requested.
   d. If ANY of (a)/(b)/(c) fails:
      - Log: `"modify_diagram sanity gate REJECT: [count mismatch: N_out=X vs N_expected=Y | missing IDs: [...] | unexpected IDs: [...]]"`
      - Discard `candidate_dsl` (keep pre-modify `current_dsl`)
      - Fall back: attempt Track B (seed exploration with `current_dsl`) or Track C (DSL rewrite); if those also fail, proceed to Track E
      - Do NOT retry `modify_diagram` with the same instruction (hallucination is likely to recur)
   e. If all pass: set `current_dsl = candidate_dsl`, proceed to step 4.5 (Structural Post-Validation).

   **Track B — Seed Exploration (for layout dissatisfaction)**:

   **layout_mode_inert short-circuit guard** (B1, fast-exit at the very top of Track B):
   Before any seed exploration or layout_mode switch decision in this Track, check the session flag `layout_mode_inert`. If `layout_mode_inert == true` (set by Step 0 Dual-Candidate Pre-Loop sub-step (b-bis) or topology pre-filter (a-pre), or set later in this same session by an in-loop identity check), first check the MCP response meta for `auto_fold_applied == true`. If auto-fold applied and `assess_quality_enhanced` score ≥ 0.7, the engine's auto-fold produced acceptable multi-row output — log `"layout_mode_inert active but auto-fold produced acceptable output; skipping Track E"` and proceed to Track A/C/D as normal (skip Track B seed exploration only). If auto-fold did NOT apply or quality < 0.7, abort Track B without consuming the 3-seed budget. Log: `"layout_mode_inert active — skipping all layout_mode/seed exploration; routing to Track E."` Record in `iteration_log` with `action="layout_mode_inert"` and `notes="Pre-loop or in-loop identity check confirmed all layout_modes produce identical output; Track B short-circuit"`. Route directly to **Track E** (hard override, identical to `edge_collision == true` routing). Rationale: when layout_mode is inert for this DSL, all DSL-level layout levers are exhausted; only Track E .tex coordinate editing can change the spatial arrangement.

   Use when: overall layout is crowded, edges cross excessively, spacing is uneven, but content is correct. Tiered trigger: quality score < 0.7 → mandatory (try at least 3 seeds); quality score 0.7–0.85 AND `view_image` reveals layout problems → mandatory (try at least 2 seeds); quality score unavailable AND visual issues present → treat as < 0.7.
   Additional trigger: bounding box aspect ratio < 0.3 (extremely narrow-tall) or > 3.0 (extremely wide-flat) as observed from `view_image` or `assess_quality_enhanced` → mandatory seed exploration (try at least 3 seeds), regardless of quality score.
   ```
   tikz-writer/generate_diagram(content=<current_dsl>, seed=<new_seed>, ...)
   → Run assess_quality_enhanced on both old and new → pick higher score
   → Update current_dsl if new seed is better
   ```
   Try at least seeds 7, 123, 999 before concluding layout cannot improve.

   **Δ early-stop check** (per new seed):
   After each new seed generation, run `assess_quality_enhanced` and compute:
     - `Δoverall    = overall_new - overall_prev`
     - `Δreadability = readability_new - readability_prev`
   (First new seed has no prev — skip Δ check on round 1, take effect from round 2.)
   If `Δoverall < 0.005 AND Δreadability < 0.005`: mark this seed as "no-op exploration" in `iteration_log` and do NOT count it toward the 3-seed budget. After **2 consecutive no-op seeds**, abort Track B and switch to **layout_mode exploration**:
     Before performing the layout_mode switch, re-check `layout_mode_inert`; if true at this point (e.g., set by mid-loop identity comparison against an earlier layout_mode entry in iteration_log), skip the switch and route to Track E (same behavior as the top-of-Track-B guard above).
     - If current `layout_mode` is `"standard"`, retry with `layout_mode="compact"` (or vice versa).
     - If both modes have been tried, route to **Track D** (topology transform).

   **Seed-invariant detection** (fast-exit, evaluated on the FIRST Δ check — round 2 of Track B):
   If `Δoverall == 0 AND Δreadability == 0` (exact zero, NOT merely < 0.005), set `seed_invariant = true`. Log: `"DSL is seed-invariant (typical for <12-node simple topologies) — skipping remaining seed exploration."` Immediately abort Track B and route to **Track D** (topology transform) WITHOUT requiring a second no-op confirmation. Rationale: exact-zero Δ across two distinct seeds (e.g., 42→7) indicates the layout engine deterministically places nodes for this DSL regardless of seed; further seed exploration is futile. Record this round in `iteration_log` with `action="seed-invariant"`.

   **Scope**: `seed_invariant` is layout_mode-scoped. Conceptually maintain a set `seed_invariant_modes: set[layout_mode]`; when this fast-exit fires, add the current layout_mode to the set. The fast-exit only triggers if the current layout_mode is already in the set; for a layout_mode never tested, run seed exploration normally even if a different mode was previously marked invariant. On every layout_mode switch (handled in **layout_mode monotonicity guard** and **layout_mode auto-degradation handler**), do NOT carry the previous mode's invariant flag — the new mode must independently demonstrate seed-invariance via its own Δ check before being skipped.

   **layout_mode monotonicity guard** (after every layout_mode switch):
   Before switching, snapshot `prev_overall = iteration_log[-1].overall` AND `prev_layout_mode = iteration_log[-1].layout_mode` (call this the rollback baseline). After the switched-mode generate completes, compute `Δoverall = new_overall - prev_overall`.
     - If `Δoverall < -0.05` (strict less than negative 0.05): immediately ROLLBACK —
       1. Restore `current_dsl` to the last entry in `iteration_log` with `layout_mode == prev_layout_mode`.
       2. If no `.tex` cache exists, regenerate with `prev_layout_mode` + same seed (one extra MCP call).
       3. Record in `iteration_log`: `action="layout_switch_rollback"`, `notes="Δoverall=<value> < -0.05, reverted to <prev_layout_mode>"`.
       4. Do NOT retry the same switch this round; route to **Track D**.
     - If `-0.05 ≤ Δoverall < 0.005`: switch is no-op (already covered by Δ early-stop above).
     - If `Δoverall ≥ 0.005`: switch is productive, continue normal iteration. On a productive switch, reset `seed_invariant` for the new layout_mode (per **Seed-invariant detection Scope** rule). Additionally, if at this point `layout_mode_inert` is true (rare — would imply a productive switch despite inert flag), log the inconsistency `"WARNING: productive layout_mode switch despite layout_mode_inert==true; clearing inert flag for this round"`, clear `layout_mode_inert = false`, and continue normal iteration. (Defensive branch — should not normally occur.)

   **MCP parameter verification** (when advanced layout params like `cycle_removal`, `coord_assignment`, `layout_mode` are used):
   After `generate_diagram` returns, inspect the output `.tex` file to verify the parameter took effect (e.g., for `cycle_removal="dfs_back"`, check that back-edges are rendered as dashed/annotated rather than normal edges). (This condition is rare after tikz-writer v1.1.0+ MCP fixes.) If the parameter was silently ignored:
   1. Log: "MCP parameter `<param>` not reflected in output — falling back to CLI."
   2. Switch to **CLI Fallback** (see below).

   **layout_mode-specific verification** (when `layout_mode` was explicitly set):
   - **Check 1 (Error detection)**: If MCP response contains an unrecognized-parameter error mentioning `layout_mode`, set `layout_mode_rejected = true`.
   - **Check 2 (Silent-ignore detection)**: If no error is returned, parse node `at (x, y)` coordinates from the `.tex` and compute the average pairwise spacing of adjacent nodes (Euclidean distance between consecutively-placed nodes).
     - If `layout_mode == "compact"` and average spacing > **5.0 cm**: the request was likely ignored (compact typically yields 2.5–4.0 cm; standard typically yields 5.0–7.0 cm). Set `layout_mode_rejected = true`.
     - If `layout_mode` is a non-enum value (e.g., `"serpentine"`, not in `LAYOUT_MODE_KNOWN`): inspect the coordinate pattern. If the output exhibits the same regular grid as the default `standard` layout (no row/column reversal, uniform spacing typical of standard mode), the request was likely ignored. Set `layout_mode_rejected = true`.
   - The boolean `layout_mode_rejected` is consumed by the **layout_mode auto-degradation handler** (immediately below) to trigger fallback. If `false`, no further action.

   **layout_mode auto-degradation handler** (consumes `layout_mode_rejected` from above):
   When `layout_mode_rejected == true`:
   1. Log: `"⚠️ layout_mode=<original_value> was rejected/ignored by MCP engine. Auto-degrading to 'compact'."`
   2. Re-invoke `generate_diagram` with `layout_mode="compact"`, keeping all other parameters (content, seed, aspect_ratio, etc.) unchanged.
   3. Record in the per-round summary: `{layout_mode_degraded: true, from: "<original_value>", to: "compact", reason: "MCP rejection"}`.
   4. The compact-degraded output proceeds through the normal Stage C quality gate (assess_quality_enhanced + step 3.2 / step 4.5 checks). If it passes, continue normal iteration.
   5. If the compact-degraded output **still fails** the quality gate, control passes to the **CLI Fallback** section (see below) for `layout_mode`-specific recovery.
   6. Reset `seed_invariant` for the new layout_mode (per **Seed-invariant detection Scope** rule above).
   Note: if `layout_mode == "compact"` was the original request and it was rejected, do NOT re-invoke with compact again; pass directly to CLI Fallback.

   **Track C — DSL Rewrite (for structural overhaul)**:
   Use when: major hierarchy reorganization, diagram type change, starting over.
   Agent manually edits DSL → `tikz-writer/validate_dsl` → `tikz-writer/generate_diagram`.
   → Update current_dsl

   **Track D — Layout Topology Transform (for shape mismatch)**:
   Use when: diagram is topologically linear/sequential but rendered as narrow-tall or wide-flat, mismatching the target aspect ratio. Content and connections are correct; only the spatial arrangement needs restructuring.
   Diagnosis: longest chain in the graph has > 6 nodes AND the bounding box aspect ratio deviates > 2× from the target aspect ratio (e.g., target is ~4:3 but output is ~1:5). If `assess_quality_enhanced` does not provide quantitative aspect/chain data, diagnose via `view_image` visual inspection (fallback).
   Candidate strategies (try in order until aspect improves):
     1. **Dual-column**: split chain at midpoint, route second half as a parallel column connected by a return edge.
     2. **Z-shape / serpentine**: fold the chain every N nodes (N ≈ ceil(sqrt(total_nodes))), alternating left-to-right and right-to-left rows.
     3. **Grouped clusters**: identify semantic subgroups within the chain and layout as clustered blocks with inter-group edges.
     4. **Manual row partitioning + multi_column** (column-order constraint via DSL declaration order): When the user requires a specific column count or column-content mapping that the engine's automatic placement does not honor — agent manually partitions the linear chain into row groups by reordering DSL node declarations, then sets `layout_mode="multi_column"`. Procedure:
        - Choose `cols ≈ ceil(sqrt(N))` (default) or use user-specified column count.
        - Compute `rows = ceil(N / cols)`.
        - Reorder DSL NODE declarations so that nodes 1..cols form row 0, nodes cols+1..2*cols form row 1, etc. (multi_column engine reads NODE order as row-major placement).
        - Re-emit EDGE declarations unchanged (engine routes around the new layout).
        - Generate with `layout_mode="multi_column"` and `aspect_ratio` chosen to match `cols × rows` aspect (e.g., 4×3 grid → `aspect_ratio="4:3"`).
        - This strategy uses only DSL node-declaration order and does NOT rely on DSL `GROUP`/`ROW` keywords (which may not be supported by the current tikz-writer DSL grammar). If the engine ignores the row partitioning and still produces a poor layout, the existing **layout_mode auto-degradation handler** will fall back to compact mode automatically.
   Implementation: restructure DSL node positions/groups to apply chosen strategy → `tikz-writer/validate_dsl` → `tikz-writer/generate_diagram` with matching `aspect_ratio`.
   → Update current_dsl

   **Track E — Direct .tex Coordinate Editing (precision fallback for spatial control beyond engine capability)**:
   Use when: user needs exact node positioning — multi-column, serpentine, grid, Z-shape, or custom coordinate layouts; or layout requirement matches a Known Limitations DSL-unsolvable item; or Tracks A–D have been attempted ≥ 2 times and cannot achieve the target layout. This is a precision fallback for spatial arrangements that the DSL layout engine cannot produce to sufficient quality.
   Trigger: (a) explicit multi-column/serpentine/grid/Z-shape request; (b) Known Limitations DSL-unsolvable match; (c) ≥ 2 failed Track A–D attempts on the same layout issue.
   Procedure (two-layer: MCP-seeded fine-tune primary, from-scratch coordinate rewrite fallback):

   **Primary: MCP-seeded fine-tune** (R6-validated path — start from MCP serpentine output, apply targeted fixes):
     1. Identify the `.tex` file path from the most recent `generate_diagram` output (`tex_file` field). If no `.tex` exists (MCP did not produce output), skip to **Fallback** below.
     2. Read the `.tex` file content using `read_file`. Verify that the output topology is correct: all expected nodes are present and connections match the intended graph. If the topology is fundamentally wrong (missing nodes, wrong connections), skip to **Fallback** below.
     2.5. **Verify soft provenance marker**: Check if the `.tex` contains `% tikz-writer:soft v1`. If missing (e.g., the MCP-generated `.tex` was subsequently modified and the marker was stripped), insert it on the line immediately after `\documentclass[...]`. This ensures `export_high_resolution` recognizes the file and bypasses strict TeX safety checks for `\input` commands.
     3. **Clean virtNodes**: Search for and delete:
        - `\node` declarations where the label is empty (`{}`) or the node ID contains a `virt`/`phantom`/`dummy` prefix (e.g., `\node[...] (virt_1) at (x,y) {}`)
        - `\coordinate (_v\d+)` lines (regex: `^\s*\\coordinate\s*\(_v\d+\)`)
        - All `\draw`/`\path` segments that reference deleted node IDs or `_v\d+` coordinates (regex: lines containing `(_v\d+)` in path expressions)
        After cleanup, verify remaining `\draw` lines reference only named real nodes (no `_v` coordinate references). If any `_v` reference remains in a `\draw` line, delete that entire `\draw` command.
     4. **Fix edge routing direction**: In serpentine layouts, even rows (0-indexed) should flow L→R and odd rows should flow R→L. For each `\draw[->] (nodeA) -- (nodeB)` or similar edge declaration, compare the x-coordinates of the source and target nodes. If a node pair is on an odd row but the source x < target x (i.e., direction is L→R instead of the expected R→L), swap the source and target in the `\draw` command.
     5. **Adjust spacing**: Check that node y-coordinates are evenly spaced across rows and x-coordinates are evenly spaced within each row. Micro-adjust `at (x, y)` values to align nodes to a uniform grid.
     5.5. **Edge-through-node collision validation** (same procedure as Fallback step 5.5 below): After adjusting spacing, verify no edge path passes through an unrelated node. Apply y-offset waypoint fixes if collisions are detected (max 3 iterations).

   **Fallback: From-scratch coordinate rewrite** (when MCP-seeded fine-tune is inapplicable — topology wrong or no .tex output):
   Trigger: (a) `generate_diagram` did not produce a `.tex` file; (b) MCP output topology is fundamentally wrong (missing nodes, incorrect connections, virtNode cleanup insufficient) as determined in Primary step 2.
     1. Identify the `.tex` file path from the most recent `generate_diagram` output (or create a minimal `.tex` scaffold from the DSL).
     2. Read the `.tex` file content using `read_file`.
     3. Identify TikZ `\node` coordinate declarations (`at (x, y)`) and `\draw`/`\path` edge definitions.
     4. Manually edit node coordinates `at (x, y)` to achieve target layout using the coordinate templates below.
     4.5. **Inject soft provenance marker**: Insert `% tikz-writer:soft v1` on the line immediately after `\documentclass[...]`. This is MANDATORY for Track E Fallback files — they are not produced by `render()` and therefore lack the marker that `render()` automatically appends (render.py:L4923). Without this marker, `export_high_resolution` will reject the file due to `\input{styles/...}` matching the strict TeX safety regex.

    **Template Selection Heuristic** (applied when entering Track E Fallback, or when Primary step 3/4/5 needs to recompute layout from scratch):
    1. **Satellite detection**: Identify satellite nodes — any node with `in_degree == 0 AND out_degree == 1` whose single target is a chain node (chain = nodes reachable via the primary edge traversal). Exclude satellite nodes from the chain for layout purposes.
    2. **Chain node count**: `N_chain = total_real_nodes - satellite_count`.
    3. **Column count**: `cols = ceil(sqrt(N_chain))`. Clamp: `cols = max(2, min(cols, 5))`.
    4. **Template selection**: `cols == 2` → 2-column template; `cols == 3` → 3-column template; `cols >= 4` → serpentine template with `cols_per_row = cols`.
    5. **Spacing defaults**: `col_spacing = max(4.0, max_label_width_cm + 1.5)`, `row_spacing = max(3.5, max_label_height_cm * 2 + 2.0)`. When label dimensions are unknown, use `col_spacing = 4.5`, `row_spacing = 4.0`.
    6. **Satellite placement**: For each satellite node, place at `(target_x + col_spacing, target_y - row_spacing / 3)` — offset to the right and slightly above its target node. If that position overlaps an existing node, try `(target_x - col_spacing, target_y - row_spacing / 3)` (left side). Draw edge from satellite to target as a straight line.
    7. **Back-edge routing**: For any back-edge (target has lower topological order than source), route as dashed line outside the bounding box: `(source.east) -- (bbox_right + 1.5, source_y) -- (bbox_right + 1.5, target_y + 1.2) -- (target_x, target_y + 1.2) -- (target.north)` with `rounded corners=8pt`. Place label at midpoint of the rightmost vertical segment.

   **Coordinate Templates** (parametric — adapt `col_spacing`/`row_spacing` to actual node size, typical range 3.0–5.0 cm):

   For each template, let `i` = 0-based node index in the desired traversal order.

   - **2-column layout**:
     ```
     col = i % 2;  row = i // 2
     x = col * col_spacing;  y = -row * row_spacing
     ```
     Edge direction: → within each row; ↓ between rows (right node of row `r` → left node of row `r+1`)

   - **3-column layout**:
     ```
     col = i % 3;  row = i // 3
     x = col * col_spacing;  y = -row * row_spacing
     ```
     Edge direction: → within each row; ↓ from last column of row `r` to first column of row `r+1`

   - **Serpentine (Z-shape) layout** (`cols_per_row` = number of columns per row, typically `ceil(sqrt(N))`):
     ```
     row = i // cols_per_row
     col = (i % cols_per_row) if row % 2 == 0 else (cols_per_row - 1 - i % cols_per_row)
     x = col * col_spacing;  y = -row * row_spacing
     ```
     Edge direction: → on even rows, ← on odd rows; ↓ between rows (last node of row `r` → first node of row `r+1`, where "first" follows the row's direction)

     5. Save edits using `replace_string_in_file` or `multi_replace_string_in_file`.
     5.5. **Edge-through-node collision validation**: Parse all `\draw`/`\path` commands and `\node` coordinates from the saved `.tex`. For each edge path, extract polyline segments and verify no intermediate segment intersects an unrelated node's bounding box (node center ± `minimum width/2`, `minimum height/2`; default 1.5cm × 0.8cm).
        - If collision found: adjust the routing by inserting a TikZ coordinate waypoint that offsets the edge path by `collider_half_height + 0.3cm` in the direction away from the collider node (e.g., `(source) -- ++(0, offset) -- (target)` or equivalent `|- / -|` routing).
        - Re-save the `.tex` with the adjusted routing.
        - Re-run collision detection on the modified path. Repeat up to 3 iterations. If collisions persist after 3 iterations, log `"Edge collision auto-fix exceeded 3 iterations — manual routing recommended"` and proceed to step 6 (the collision will be visible in the preview for manual correction).
     6. Recompile: run `pdflatex <file>.tex` (or `xelatex` for Chinese content) in terminal. If the compile command is unavailable, attempt `tikz-writer/export_high_resolution` with the `.tex` file path as fallback. If compilation fails, read the `.log` file to diagnose and fix; retry up to 3 times before falling back to the last successful version.
        - **compile_env note (A5)**: If the `.tex` contains relative `\input{...}` references (typical for tikz_writer-generated files that pull in `styles/base_style.tex`), set `TEXINPUTS` so the style files resolve. tikz_writer convention: `TEXINPUTS=".:<tex_dir>:<tex_dir>/styles:" xelatex -output-directory=<tex_dir> <tex_file>`. The MCP `export_high_resolution` path now auto-mirrors `\input{...}` refs into a temp dir (S5/T3.1), but direct shell invocations still need the env var. When emitting a Track E `.tex`, prepend a 1-line header comment: `% compile: TEXINPUTS=".:./styles:" xelatex <file>.tex` so the convention is self-documenting. Other projects may need different paths; this is the tikz_writer convention.
        - **Track E 编译命令模板**（从 workspace_root 执行，适用于 tikz_writer 项目）：
          ```
          cd <workspace_root>
          TEXINPUTS="./styles:./output/build:" pdflatex \
              -output-directory=output/build \
              -interaction=nonstopmode \
              output/build/<diagram_name>.tex
          ```
          平台差异：Linux/macOS 用 `:` 分隔；Windows PowerShell 用 `;`。
          若 `.tex` 引用 `\input{styles/...}`，必须从 workspace_root 启动以匹配相对路径。
     6.1. **Legend inline check**: After compilation, check the LaTeX log or PDF metadata for page count (`Output written on ... (N pages)`). If `N > 1` AND the `.tex` contains a separate `\begin{tikzpicture}[baseline]` block with legend node IDs (identified by nodes named `leg_io`, `leg_data`, `leg_process`, `leg_decision`, or similar `leg_*` pattern):
        a. Compute `y_min` = minimum y-coordinate among all `\node` declarations in the main tikzpicture.
        b. Move the legend `\node` declarations into the main tikzpicture, repositioned at `y = y_min - 1.5` (1.5 cm below the lowest diagram node). Distribute legend items horizontally with 1.6 cm spacing starting at `x = 0`.
        c. Delete the entire standalone legend `\begin{tikzpicture}[baseline] ... \end{tikzpicture}` block.
        d. Recompile and verify `N == 1` page output. If still multi-page, log warning and proceed (the legend placement may need manual adjustment).
        If no separate legend block exists or page count == 1: skip this step.
     7. Convert to PNG for review: run `convert -density 150 <file>.pdf <file>.png`, or use `tikz-writer/export_high_resolution` if ImageMagick is not available.
     8. Create preview (max 2000px) → `view_image` for visual check.
   Post-edit: Do NOT feed the edited `.tex` back into `modify_diagram` — the DSL state and `.tex` are now diverged. Mark `current_dsl` as `STALE` and note that further modifications require either re-extracting DSL from the `.tex` or continuing via Track E.
   → This track does NOT update `current_dsl`.

   **Track E Continuation (when `current_dsl` is STALE)**:
   Once Track E has been executed, subsequent fine-tuning stays in .tex space:
   1. Read current `.tex` with `read_file` → identify the coordinates/edges to adjust.
   2. Apply changes with `replace_string_in_file` or `multi_replace_string_in_file`.
   3. Recompile (`pdflatex`/`xelatex`).
   3.1. **Legend inline check**: After recompilation, run the same legend inline check from Track E step 6.1 before generating the final preview. If a separate standalone legend page exists, move `leg_*` nodes into the main tikzpicture at `y_min - 1.5`, delete the standalone legend block, recompile, and verify single-page output.
   3.2. Generate PNG → create preview (max 2000px) → `view_image`.
   4. Quality assessment in STALE mode: pass `diagram_path=<compiled_png_or_pdf>` to `assess_quality_enhanced` for image-level quality metrics. Supplement with `view_image` for visual judgment (spacing, overlap, alignment, readability).
   4-bis. **STALE mode .tex-level collision check** (supplements image-level `assess_quality_enhanced`):
      Parse all `\node[...] (...) at (x, y) {...}` declarations from the `.tex`. For each node, compute AABB as `[x - text_width/2, x + text_width/2] × [y - 0.4, y + 0.4]` (text_width from the node's `text width=Ncm` style option; default 1.8cm. Height default 0.8cm). Check pairwise AABB overlap. Report overlaps in iteration log. If overlap detected, apply coordinate micro-adjustments before recompiling. If `.tex` coordinate parsing fails (e.g., `\foreach` macro expansion), skip with log: `"tex-level collision check skipped — coordinate parsing failed"`.
   5. Repeat steps 1–4 for each adjustment round.
   6. **Convergence detection**: Track the `.tex` edit delta across consecutive rounds. If 3 consecutive rounds produce only cosmetic changes (coordinate adjustments ≤ 0.2cm AND no node additions/removals AND no edge structural changes), set `track_e_converged = true` and log "Track E base converged — layout mature."
   6.5. **Base fixation** (formal snapshot of the converged base — see also `skills/track-e-tex-editing/SKILL.md` Phase 4 step 6.5):
      Trigger: `track_e_converged == true` (set in step 6) **AND** the next iteration round (the 4th consecutive cosmetic-only round) also satisfies the cosmetic-only criteria. In other words, fixation requires 3 rounds to set the convergence flag plus 1 additional stable round = 4 consecutive stable rounds total.
      Steps:
         a. Copy the current `.tex` to `<basename>_fixated_base.tex` (file-level snapshot, not just a flag).
         b. Record fixation metadata: `{fixated_round: <R>, quality_score: <readability_score>, node_count: <N>, edge_count: <E>, timestamp: <ISO-8601>}`.
         c. Log: `"Track E base fixated at round <R>. Subsequent rounds will check regression against fixated base."`
         d. If the `.tex` file is missing or unreadable at fixation time, log `"⚠️ Cannot fixate base — .tex missing or unreadable."` and skip fixation; iteration continues normally.
      Regression check (applied in subsequent iteration rounds, before applying step 2 edits):
         - Diff the current `.tex` against `<basename>_fixated_base.tex`.
         - If the proposed edit would remove a node/edge present in the fixated base, OR shift any retained node by > 1.0cm in either x or y: log `"⚠️ Proposed edit regresses from fixated base (node deletion / edge deletion / coordinate shift > 1.0cm) — review before applying."`
         - The warning is informational only — it does NOT auto-block the edit (the user may intentionally restructure). Display a brief regression summary so the user can choose to revert toward the fixated base or proceed.
      Re-fixation: when the user explicitly requests "re-fixate base" (e.g., after intentional restructuring), overwrite `<basename>_fixated_base.tex` with the current `.tex` and refresh the metadata block. The previous snapshot is replaced (not versioned).
   7. **Engine capability verification** (when `track_e_converged`):
      a. Regenerate from scratch via MCP: `generate_diagram(content=<original_spec>, seed=<best_known_seed>)`. Try at least 3 seeds.
      b. Run `assess_quality_enhanced` on both the MCP output and the current Track E baseline. Extract `readability_score` for both.
      c. Check MCP output against MCP Sufficiency Gate conditions (3) and (4): apply the **composite quality judgement** from the Sufficiency Gate — primary `overall ≥ 0.80 AND label_collisions ≤ 2 AND no_truncation`, OR backward-compatible `readability_score ≥ 0.45 AND label_collisions ≤ 2` — AND `label_collision_free` (run the label collision detection logic from step 3.2(g) on MCP `.tex` output). Conditions (1) `topo_flow_violation` and (2) `edge_collision` also apply — run step 3.2(d) and 3.2(f) checks on MCP output.
      d. If MCP passes the gate AND overall quality ≥ Track E baseline: log "Engine capability verified — MCP produces equivalent quality for this layout." Exit STALE mode: adopt MCP output as new `current_dsl`, resume DSL-based iteration.
      e. If MCP is inferior: log "Engine capability gap persists (MCP readability={score}, baseline={baseline_score})." Continue with Track E base.
      f. Record verification outcome in per-round summary for trend tracking.
   Returning to DSL track: requires manually re-extracting DSL from the `.tex` file (labor-intensive, error-prone). Avoid frequent Track E ↔ DSL switching; commit to .tex-level iteration once Track E is entered.

   **CLI Fallback** (rare — MCP parameter pass-through has been fixed):
   **Note**: As of tikz-writer v1.1.0+, MCP correctly passes advanced layout parameters (`cycle_removal`, `coord_assignment`, etc.). This CLI fallback is retained as a safety net for rare regression scenarios. In normal operation, MCP is fully reliable and CLI fallback should almost never activate.
   MCP is always the preferred path. CLI fallback activates only when MCP parameter verification (above) detects that a parameter was ignored, or when MCP returns an unrecognized-parameter error.
   Procedure:
     1. Write `current_dsl` to a temp file: `mkdir -p /tmp/tikz-writer-cli && cat > /tmp/tikz-writer-cli/input.dsl`
     2. Invoke CLI with full parameters (see `instructions/tikz-writer-tools.instructions.md` § CLI Fallback Reference for the MCP→CLI parameter mapping):
        ```
        /home/gw/opt/tikz_writer/.venv/bin/diagram render \
          --dsl /tmp/tikz-writer-cli/input.dsl \
          --cycle-removal <value> --seed <seed> \
          --pdf --format png --out-dir /tmp/tikz-writer-cli/output
        ```
        (Adjust path if `which diagram` returns a different location.)
     3. Read the output `.tex`/`.pdf`/`.png` from the output directory.
     4. Mark `current_dsl` as STALE (CLI output is a rendered artifact, not a DSL round-trip). Subsequent modifications follow Track E Continuation or re-extract DSL manually.
   This fallback inherits all Track E post-edit rules: do NOT feed CLI output back into `modify_diagram`.

   **layout_mode-specific CLI fallback path** (extends the procedure above):
   Trigger: `layout_mode_rejected = true` (from MCP layout_mode-specific verification) **AND** the compact auto-degraded output (Task 1.3 handler) failed the Stage C quality gate.
   Steps:
     1. Write `current_dsl` to `/tmp/tikz-writer-cli/input.dsl`.
     2. Invoke CLI with the **originally requested** `layout_mode` value (not compact):
        ```
        /home/gw/opt/tikz_writer/.venv/bin/diagram render \
          --dsl /tmp/tikz-writer-cli/input.dsl \
          --layout-mode <original_value> --seed <seed> \
          --pdf --format png --out-dir /tmp/tikz-writer-cli/output
        ```
        Example for serpentine:
        ```
        /home/gw/opt/tikz_writer/.venv/bin/diagram render \
          --dsl /tmp/tikz-writer-cli/input.dsl \
          --layout-mode serpentine --seed 42 \
          --pdf --format png --out-dir /tmp/tikz-writer-cli/output
        ```
     3. If CLI succeeds and the output passes the Stage C quality gate → adopt the CLI output and mark `current_dsl` as STALE. Continue iteration in Track E Continuation mode.
     4. If CLI also rejects the value or the output fails the quality gate, apply terminal fallback by value:
        - **`serpentine`**: route to **Track E Phase 2 from-scratch coordinate template** (Phase 2 serpentine template — 8-round validated, see `skills/track-e-tex-editing/SKILL.md` Phase 2 → Coordinate Templates → Serpentine). Log: `"CLI also rejected layout_mode=serpentine — falling back to Track E coordinate template."`
        - **Any other value** (e.g., a hypothetical future `circular`, `radial`): route to the compact-degraded output already produced in Task 1.3 as the final adopted result. Log: `"CLI also rejected layout_mode=<value> — adopting compact degradation as final fallback."`
   Notes:
     - The CLI's currently supported `layout_mode` values (`standard`, `compact`) match the MCP-side enum. This fallback path is forward-compatible: when tikz-writer adds new values (e.g., `serpentine`) on the CLI side ahead of the MCP side, this path will automatically capture them.
     - Upgrade chain (single-direction, no loops): MCP → compact auto-degradation → CLI with original value → Track E (serpentine) / compact (others).

4.5. **Structural Post-Validation** (applies to ALL tracks after execution):
   a. Parse the returned DSL: count total nodes (`N_out`) by counting NODE/node declaration lines, and edges (`E_out`) by counting EDGE/connection declaration lines.
   b. Compare against the expected counts:
      - **Track A (modify)**: `N_expected` = pre-modify count ± explicitly requested additions/removals. `E_expected` = similar.
      - **Track B (seed)**: `N_expected` = same as previous iteration (seed change must not alter node/edge count). `E_expected` = same.
      - **Track C/D/E (restructure)**: `N_expected` = user specification or previous iteration count. Deviation is expected; proceed to (c) as WARNING not REJECT.
   c. Decision:
      - If `N_expected ≤ 5`: use absolute threshold — **REJECT** if `|N_out - N_expected| > 1` (Track A/B) or unexpected new node IDs appear.
      - If `N_expected > 5`: use percentage threshold — **REJECT** if `|N_out - N_expected| / N_expected > 0.2` OR unexpected new node IDs appear (Track A/B).
      - On REJECT: log the discrepancy, discard returned DSL, fall back to next Track in priority (A→B→C→E).
      - If Track C/D/E and deviation > 0.2 (or > 1 for small graphs): **WARN** in iteration summary, but proceed; request user confirmation if deviation > 0.5.
      - Otherwise: **PASS**, update `current_dsl`.
   d. Log validation result (PASS/WARN/REJECT + counts) in iteration summary.

5. Preview: `image-worker/resize_image` (generate a max-2000px preview copy) → `view_image` (inspect the preview copy, not the full-size source).
6. Summarize each round: what changed, what improved, what remains. Append the entry to `iteration_log` per the schema in Stage C header (round, track, seed, layout_mode, overall, readability, label_collisions, delta_overall, delta_readability, action, notes, warnings, collision_counts).
7. Stop when:
   - user accepts,
   - two consecutive rounds show no meaningful gain,
   - **light-collision fast-pass**: `label_collisions ≤ 2 AND readability_score ≥ 0.40 AND topo_flow_violation == false AND edge_collision == false` → deliver as-is without forcing Track E. Log the fast-pass reason in `iteration_log` (action="fast-pass").
   - **unreachable declaration**: after 5 rounds with `iteration_log` showing
       (a) ≥ 3 distinct `seed` values tried AND
       (b) ≥ 1 `layout_mode` switch AND
       (c) latest entry still fails Sufficiency composite (`overall < 0.80` OR `label_collisions > 2`) AND fails OR-fallback (`readability < 0.40`) AND fails collision-free path (`collision_warning_detected == true` OR `label_collision_free == false`)
     → produce a "known-unreachable" declaration:
       1. deliver the best-effort version (entry with highest `overall` in `iteration_log`).
       2. emit declaration: `"Quality target unreachable within 5 rounds. Best overall = {value} at round {R}. Limiting factors: [list top 2 from get_optimization_advice]."`
       3. ask user: `"Continue manual iteration / switch to Track E / accept best-effort?"`
     Do NOT auto-terminate; await user decision. (5 rounds is a soft upper bound — user may accept current result at any earlier round.)
   - or max rounds reached.

### Stage C.5: Pattern B Depth Escalation (New — Sequential Self-Review)

Before finalization, execute **Pattern B sequential depth escalation** on the current diagram:

| Level | Scope | Checks | Blocking Threshold |
|-------|-------|--------|-------------------|
| **Quick** | Visual clarity | Node/edge overlap, label readability, color contrast, font size uniformity, whitespace balance, preview visual check (`view_image`) | 0 blocking issues |
| **Medium** | Structural correctness | Connection accuracy, hierarchy/flow direction correct, all referenced elements present, legend completeness, axis/scale labels correct (for data plots) | 0 blocking issues |
| **Thorough** (Optional*) | Journal compliance | Venue-specific size/aspect constraints, font family/typeface rules, color mode (grayscale-safe for print), export DPI target met | 0 blocking issues |

*Thorough level executes only if target journal is known and has explicit diagram specs, or user explicitly requests.

#### C.5a: Escalation Rules

1. **Quick always executes first.** Any visual issue → fix ALL → restart from Quick (re-render + re-view).
2. Quick passes → escalate to Medium.
3. Medium ≥3 issues → fix ALL → restart from Quick. Medium 1-2 issues → fix → re-run Medium.
4. Medium passes → escalate to Thorough (if triggered).
5. Thorough failure → fix ALL → restart from Quick.
6. **Max 3 full restart cycles.** After 3 cycles → degrade: deliver Quick+Medium-pass version with "⚠️ Thorough not passed."
7. **Issue Ledger**: Maintain a running ledger of all issues found (fingerprinted by level + category + location context + key terms). On each restart, carry the ledger forward. Only report issues that are (a) still present from a previous cycle, or (b) genuinely new. If open issue count increases between cycles (non-monotone drift), halt escalation and deliver the previous cycle's output with annotation "⚠️ Non-monotone drift detected — delivering prior-cycle version." See `docs/cross-validation-patterns.md` §Issue Ledger Protocol for full specification.

#### C.5b: Cross-Validation Gate Check

After Pattern B passes or degrades: output `[Cross-Validation Gate: Pattern B PASS]` or `[Cross-Validation Gate: DEGRADED — Thorough not passed]`.

### Stage D: Finalization & Export

1. If journal preset not applied yet and journal is known, apply with `tikz-writer/apply_journal_preset`.
2. Export using `tikz-writer/export_high_resolution` with scene-matched preset:

   | Scene | preset | format | DPI | Notes |
   |-------|--------|--------|-----|-------|
   | IEEE journal | `ieee` | `pdf` | 600 | `embed_fonts=true` |
   | Nature / high-end publication | `professional` | `pdf` | 1200 | `embed_fonts=true` |
   | Print document / patent | `print` | `pdf` | 300 | |
   | Slides / screen | `screen` | `png` | 96 | |
   | Web / documentation | `web` | `svg` | 150 | SVG optimized |

   If custom DPI is needed, set `dpi` parameter to override the preset default.
3. Preserve and deliver editable source (DSL and/or generated `.tex`).
4. Before final visual check, create a max-2000px preview copy with `image-worker/resize_image`, then perform `view_image` on that preview.

### Stage E: Delivery

-1. **Mandatory final visual check**: Before delivery, create a max-2000px preview copy with `image-worker/resize_image` → `view_image` on the preview. This step **MUST NOT be skipped** regardless of structured field collision counts — all-zero collision fields do not guarantee visual correctness (rendering artifacts, font substitution, label clipping, and whitespace distribution are only detectable visually). If `image-worker` is unavailable, fall back to direct `view_image` on the output file (accept potential API size-limit warnings). This applies even when Stage C fast-pass or Step 0 dual-candidate selection bypassed Stage D's iteration-loop preview.

0. **Pre-Delivery Audit**: Execute `instructions/pre-delivery-audit.instructions.md` — L1-Lite for conceptual diagrams; L2-Standard if diagram encodes quantitative data (scales, dimensions, physical parameters). Verify axis/scale labels and units are correct. **FAIL → block delivery, fix diagram, re-audit.** Append audit table (for L1-Lite, a one-line confirmation suffices).

1. Deliver artifact list (PNG/PDF/SVG + DSL/TEX).
2. Provide quality summary from `tikz-writer/assess_quality` + `tikz-writer/assess_quality_enhanced`.
3. Provide embedding guidance for manuscript/report/slides.
4. Provide concise iteration changelog.
5. **Skill Crystallization Check**: After delivery, execute `instructions/skill-crystallization.instructions.md` trigger detection (T1/T2/T3). If any trigger fires, propose crystallization to user. If none fires, skip silently.

