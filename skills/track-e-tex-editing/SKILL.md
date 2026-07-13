---
name: "track-e-tex-editing"
description: "TikZ .tex coordinate editing for precise spatial control — multi-column, serpentine, grid, Z-shape layouts. 直接编辑 TikZ .tex 坐标实现精确空间控制, MCP-seeded fine-tune 微调, 坐标模板, 蛇形布局, 多列布局, 网格布局, virtNode 清理, edge routing 修正."
revision: 5
---

# Track E — Direct .tex Coordinate Editing

> Crystallized from: Diagram Architect Track E procedure, validated across 8 iteration rounds (R1–R8)
> Date: 2026-04-17
> Trigger: T1 (≥5 distinct tool-call steps) + T2 (≥7 occurrences in workflow-patterns)

## When to Use

- User explicitly requires precise coordinate control AND MCP Sufficiency Gate fails (readability < 0.7 or label collisions present or semantic overrides active) — the engine cannot produce sufficient quality
- Layout requirement matches a Known Limitations DSL-unsolvable item (e.g., ALIGN/ABOVE ignored, aspect_ratio canvas-only)
- Tracks A–D have been attempted ≥ 2 times and cannot achieve the target layout
- Stage C quality checks route to Track E after engine output fails to meet layout requirements
- Any scenario requiring exact node positioning that the DSL layout engine cannot produce

## When NOT to Use

- Simple node add/remove/relabel/reconnect — use Track A (`modify_diagram`) instead
- Content is wrong (missing nodes, incorrect labels) — fix content first via Track A or Track C
- DSL-level layout is satisfactory — no need for .tex editing if the engine output is acceptable
- Only layout quality is poor but content/topology correct — try Track B (seed exploration) first
- MCP Sufficiency Gate passes (readability ≥ 0.7 AND label_collision_free AND no topo_flow_violation AND no edge_collision) — the MCP path is sufficient, Track E is not needed

## Workflow

### Phase 1: MCP-Seeded Fine-Tune (Primary — try first)

1. **Identify .tex file**: Get the `.tex` file path from the most recent `generate_diagram` output (`tex_file` field). If no `.tex` exists, skip to Phase 2 (Fallback).
2. **Read and verify topology**: Read the `.tex` file using `read_file`. Verify all expected nodes are present and connections match the intended graph. If topology is fundamentally wrong (missing nodes, wrong connections), skip to Phase 2.
3. **Clean virtNodes**: Search for `\node` declarations where:
   - Label is empty (`{}`)
   - Node ID contains `virt`/`phantom`/`dummy` prefix (e.g., `\node[...] (virt_1) at (x,y) {}`)
   Delete these nodes and remove all `\draw`/`\path` edges that reference them.
4. **Fix edge routing direction**: In serpentine layouts, even rows (0-indexed) should flow L→R and odd rows should flow R→L. For each `\draw[->] (nodeA) -- (nodeB)`:
   - Determine which row each node is on (by y-coordinate)
   - If a node pair is on an odd row but source x < target x (direction is L→R instead of expected R→L), swap source and target in the `\draw` command
5. **Adjust spacing**: Check that node y-coordinates are evenly spaced across rows and x-coordinates are evenly spaced within each row. Micro-adjust `at (x, y)` values to align nodes to a uniform grid.

### Phase 2: From-Scratch Coordinate Rewrite (Fallback)

Trigger: (a) `generate_diagram` did not produce a `.tex` file; (b) MCP output topology is fundamentally wrong.

1. **Get .tex scaffold**: Identify the `.tex` file path from the most recent output, or create a minimal `.tex` scaffold from the DSL.
2. **Read .tex**: Read file content using `read_file`.
3. **Identify coordinates**: Locate TikZ `\node` coordinate declarations (`at (x, y)`) and `\draw`/`\path` edge definitions.
4. **Apply coordinate template**: Manually edit node coordinates using the templates below.

### Coordinate Templates

Parametric — adapt `col_spacing`/`row_spacing` to actual node size (typical range 3.0–5.0 cm). Let `i` = 0-based node index in desired traversal order.

**2-column layout** (most validated — stable across 8 rounds):
```
col = i % 2;  row = i // 2
x = col * col_spacing;  y = -row * row_spacing
```
Edge direction: → within each row; ↓ between rows (right node of row `r` → left node of row `r+1`)

**3-column layout**:
```
col = i % 3;  row = i // 3
x = col * col_spacing;  y = -row * row_spacing
```
Edge direction: → within each row; ↓ from last column of row `r` to first column of row `r+1`

**Serpentine (Z-shape) layout** (`cols_per_row` = number of columns per row, typically `ceil(sqrt(N))`):
```
row = i // cols_per_row
col = (i % cols_per_row) if row % 2 == 0 else (cols_per_row - 1 - i % cols_per_row)
x = col * col_spacing;  y = -row * row_spacing
```
Edge direction: → on even rows, ← on odd rows; ↓ between rows (last node of row `r` → first node of row `r+1`, where "first" follows the row's direction)

### Phase 3: Compile & Preview (applies to both Primary and Fallback)

5. **Save edits**: Use `replace_string_in_file` or `multi_replace_string_in_file`.
5.5. **Edge-through-node collision validation**: Parse all edge paths and node bounding boxes from the `.tex`. For each edge, verify no polyline segment intersects an unrelated node's bounding box (center ± half `minimum width`/`minimum height`, default 1.5cm × 0.8cm). If collision found, insert a TikZ waypoint to offset the edge by `collider_half_height + 0.3cm` away from the collider. Repeat up to 3 iterations; if collisions persist, warn and proceed to compile (manual fix via preview).
6. **Recompile**: Run `pdflatex <file>.tex` (or `xelatex` for Chinese content). If compilation fails, read the `.log` file to diagnose and fix; retry up to 3 times.
7. **Convert to PNG**: Run `convert -density 150 <file>.pdf <file>.png`, or use `tikz-writer/export_high_resolution` if ImageMagick is unavailable.
8. **Create preview**: Resize to max 2000px → `view_image` for visual check.

### Phase 4: Track E Continuation (subsequent fine-tuning in STALE mode)

Once Track E has been executed, `current_dsl` becomes STALE. Subsequent adjustments stay in .tex space:

1. Read current `.tex` with `read_file` → identify coordinates/edges to adjust.
2. Apply changes with `replace_string_in_file` or `multi_replace_string_in_file`.
3. Recompile → generate PNG → create max-2000px preview → `view_image`.
4. Quality assessment in STALE mode: pass `diagram_path=<compiled_png_or_pdf>` to `assess_quality_enhanced` for image-level metrics. Supplement with `view_image` for visual judgment.
5. Repeat steps 1–4 for each adjustment round.
6. **Convergence detection**: Track the `.tex` edit delta across consecutive rounds. If 3 consecutive rounds produce only cosmetic changes (coordinate adjustments ≤ 0.2cm AND no node additions/removals AND no edge structural changes), set `track_e_converged = true` and log "Track E base converged — layout mature."
6.5. **Base fixation** (formal snapshot of the converged base — this step is kept in sync with `diagram-architect.md` Track E Continuation step 6.5):
   Trigger: `track_e_converged == true` (set in step 6) **AND** the next iteration round (the 4th consecutive cosmetic-only round) also satisfies the cosmetic-only criteria. Fixation requires 3 rounds to set the convergence flag plus 1 additional stable round = 4 consecutive stable rounds total.
   Steps:
   a. Copy the current `.tex` to `<basename>_fixated_base.tex` (file-level snapshot, not just a flag).
   b. Record fixation metadata: `{fixated_round: <R>, quality_score: <readability_score>, node_count: <N>, edge_count: <E>, timestamp: <ISO-8601>}`.
   c. Log: `"Track E base fixated at round <R>. Subsequent rounds will check regression against fixated base."`
   d. If the `.tex` file is missing or unreadable at fixation time, log `"⚠️ Cannot fixate base — .tex missing or unreadable."` and skip fixation; iteration continues normally.
   Regression check (applied in subsequent iteration rounds, before applying step 2 edits):
   - Diff the current `.tex` against `<basename>_fixated_base.tex`.
   - If the proposed edit would remove a node/edge present in the fixated base, OR shift any retained node by > 1.0cm in either x or y: log `"⚠️ Proposed edit regresses from fixated base — review before applying."`
   - The warning is informational only — it does NOT auto-block the edit. Display a brief regression summary so the user can choose to revert or proceed.
   Re-fixation: when the user explicitly requests "re-fixate base", overwrite `<basename>_fixated_base.tex` with the current `.tex` and refresh metadata. The previous snapshot is replaced (not versioned).
7. **Engine capability verification** (when `track_e_converged`):
   a. Regenerate from scratch via MCP: `generate_diagram(content=<original_spec>, seed=<best_known_seed>)`. Try at least 3 seeds.
   b. Run `assess_quality_enhanced` on both the MCP output and the current Track E baseline. Extract `readability_score` for both.
   c. Check MCP output against MCP Sufficiency Gate conditions: `readability_score ≥ 0.7` AND `label_collision_free` AND no `topo_flow_violation` AND no `edge_collision`. Run the corresponding step 3.2 checks on MCP output.
   d. If MCP passes the gate AND overall quality ≥ Track E baseline: log "Engine capability verified — MCP produces equivalent quality." Exit STALE mode: adopt MCP output as new `current_dsl`, resume DSL-based iteration.
   e. If MCP is inferior: log "Engine capability gap persists." Continue with Track E base.
   f. Record verification outcome in per-round summary for trend tracking.

## Inputs & Outputs

| Input | Source |
|-------|--------|
| `.tex` file from `generate_diagram` output | `tex_file` field in MCP response |
| `current_dsl` (may be STALE after Track E) | Maintained across Diagram Architect iterations |
| Target layout type (2-col/3-col/serpentine/grid) | User request or Track D diagnosis |

| Output | Format |
|--------|--------|
| Edited `.tex` file | TikZ LaTeX source |
| Compiled PDF | `pdflatex`/`xelatex` output |
| Preview PNG | ≤ 2000px, for `view_image` inspection |

## Common Pitfalls

1. **virtNode identification must check both patterns**: Empty labels (`{}`) AND ID prefixes (`virt`/`phantom`/`dummy`). Missing either pattern leaves ghost nodes that break edge routing.
2. **Edge routing direction depends on row parity**: Even rows flow L→R, odd rows flow R→L. The comparison is on x-coordinates, not visual position. Always compare the numeric x values from `at (x, y)`.
3. **STALE state is irreversible (practically)**: After Track E, `current_dsl` is STALE. Do NOT feed the edited `.tex` back into `modify_diagram` — DSL state and `.tex` are diverged. Re-extracting DSL from `.tex` is labor-intensive and error-prone. Commit to .tex-level iteration once Track E is entered.
4. **MCP serpentine output was version-unstable (now stable since R6)**: Historical instability (R6→R7 regression) led to the Serpentine Quick Guard (Stage B step 3.1), which remains as a lightweight regression detector. Current engine versions (R6–R10) produce reliable serpentine output.
5. **col_spacing/row_spacing must match node size**: Typical range is 3.0–5.0 cm. Too small → overlapping nodes; too large → wasted whitespace. Inspect node width in the `.tex` style definitions before choosing spacing values.
6. **Compilation failure diagnosis**: When `pdflatex` fails, read the `.log` file — common causes are unescaped special characters (`_`, `%`, `&`) in node labels, or missing TikZ libraries. Retry up to 3 times before falling back to the last successful version.
7. **Edge-through-node collision is invisible in DSL**: The DSL layout engine does not guarantee collision-free edge routing. Always run step 5.5 after saving .tex edits. Default bounding box (1.5cm × 0.8cm) is a heuristic — inspect actual `minimum width`/`minimum height` in node styles for accuracy. Auto-fix y-offset may cascade; limit to 3 iterations.
8. **Exit STALE mode via engine verification resets current_dsl**: When step 7d adopts MCP output, subsequent Track A operations use the MCP-regenerated DSL, not the old Track E `.tex`. Verify that the new DSL correctly represents all layout requirements before continuing. If critical edits are lost, re-enter Track E.
9. **Base fixation snapshot must be updated if user changes requirements significantly**: Use "re-fixate base" to reset the snapshot. The fixated base is overwritten, not versioned — previous fixations are lost. Do not silently overwrite the fixated base during normal iterations; only overwrite on explicit user request.

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-04-17 | Initial crystallization from 7-round validated Track E procedure | Diagram Architect R1–R7 iteration experience |
| 2 | 2026-04-17 | Update to 8-round validation; 2-column template highlighted as most stable pattern | Round 8 iteration experience |
| 3 | 2026-04-17 | Added step 5.5 edge-through-node collision validation; Common Pitfall #7 | Edge collision detection requirement |
| 4 | 2026-04-18 | Simplified diagram_path (remove probe/cache), Quick Guard replaces Serpentine Validation, Track E downgraded to precision fallback | Review findings 2026-04-17 |
| 5 | 2026-04-18 | MCP Sufficiency Gate in When to Use/NOT Use, convergence detection + engine verification (steps 6–7), Common Pitfall #8 (STALE exit) | MCP-first routing plan |
| 6 | 2026-04-20 | Added step 6.5 Base fixation (4-round stability snapshot + regression check + re-fixate); Common Pitfall #9 | layout_mode degradation + Track E base fixation plan |
