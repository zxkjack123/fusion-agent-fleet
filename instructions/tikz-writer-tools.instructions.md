---
description: "tikz-writer MCP tool inventory: 14 tools with parameter quick reference, calling patterns, and common pitfalls"
applyTo: "diagram-architect,data-analyst,academic-writer,patent-writer,presentation-architect,proposal-writer,simulation-analyst,teaching-assistant"
revision: 1
---

# tikz-writer MCP Tool Inventory

## Tool Quick Reference (14 tools)

### Core

| Tool | Required Params | Key Optional Params |
|------|----------------|---------------------|
| `generate_diagram` | `content` | `content_type`, `theme`, `format`, `language`, `layout_mode`, `seed`, `aspect_ratio`, `aspect_mode`, `auto_purpose`, `tree_layout`, `tree_child_order`, `nudge_overlaps`, `cycle_removal`, `layer_assignment`, `coord_assignment`, `no_legend`, `strict` |
| `list_themes` | — | — |
| `validate_dsl` | `dsl_content` | — |
| `modify_diagram` | `modification`, `current_dsl` | `model`, `render`, `theme`, `format`, `language`, `seed`, `output_path`, `workspace_root` |

### Quality & Optimization

| Tool | Required Params | Key Optional Params |
|------|----------------|---------------------|
| `assess_quality` | `dsl_content` | — |
| `assess_quality_enhanced` | `dsl_content` | `theme` |
| `get_optimization_advice` | `dsl_content` | `theme` |

### Journal & Template

| Tool | Required Params | Key Optional Params |
|------|----------------|---------------------|
| `list_journal_presets` | — | — |
| `get_journal_requirements` | `journal` | — |
| `apply_journal_preset` | `journal`, `dsl_content` | `format`, `output_path` |
| `list_purpose_templates` | — | — |
| `apply_purpose_template` | `template_id`, `dsl_content` | `output_path`, `workspace_root` |

### Export & Diagnostics

| Tool | Required Params | Key Optional Params |
|------|----------------|---------------------|
| `export_high_resolution` | `input_file` | `preset`, `format`, `dpi`, `embed_fonts`, `output_path` |
| `doctor` | — | — |

## Export Presets

| Preset | DPI | Best For |
|--------|-----|----------|
| `screen` | 96 | Preview |
| `web` | 150 | Web + SVG |
| `print` | 300 | Print |
| `ieee` | 600 | IEEE journal |
| `professional` | 1200 | Publication |

Custom `dpi` parameter overrides preset default when set.

## Layout Tuning Parameters (generate_diagram)

| Param | Values | When to Use |
|-------|--------|-------------|
| `layout_mode` | `standard`, `compact` | `compact` for ≥15 nodes or dense connectivity |
| `tree_layout` | `auto`, `off`, `tidy` | force `tidy` for known tree structures |
| `tree_child_order` | `id`, `label` | control child node sorting |
| `seed` | integer | change seed to explore different layouts |
| `aspect_ratio` | `16:9`, `4:3`, float | match slide/column aspect |
| `aspect_mode` | `fit`, `fill`, `none` | scaling behavior within aspect box |
| `auto_purpose` | boolean | let engine pick diagram type template |
| `nudge_overlaps` | boolean | micro-adjust overlapping nodes |
| `cycle_removal` | `simple`, `dfs_back`, `none` | strategy for cyclic graphs |
| `layer_assignment` | `bfs`, `longest_path` | layer assignment algorithm |
| `coord_assignment` | `parents_bary`, `sequential`, `children_bary` | X-coordinate assignment |
| `language` | `en`, `zh` | `zh` triggers XeLaTeX engine |

## Common Calling Patterns

### Pattern: Iterative Modification (preferred for local changes)

```
1. generate_diagram(content=..., seed=42) → initial version + DSL
2. modify_diagram(modification="move Database right of API", current_dsl=<DSL from 1>)
   → updated DSL + rendered output
3. modify_diagram(modification="add Cache node between...", current_dsl=<DSL from 2>)
   → repeat, always passing latest DSL
```

### Pattern: Seed Exploration (for layout optimization)

```
1. generate_diagram(content=..., seed=42)  → version A
2. generate_diagram(content=..., seed=7)   → version B
3. generate_diagram(content=..., seed=123) → version C
4. assess_quality_enhanced on each → pick highest score
```

### Pattern: Journal Adaptation

```
1. get_journal_requirements(journal="ieee") → specs
2. generate_diagram(content=..., theme="ieee_enhanced")
3. apply_journal_preset(journal="ieee", dsl_content=<DSL>)
4. export_high_resolution(input_file=..., preset="ieee", embed_fonts=true)
```

## Common Pitfalls

- `modify_diagram` requires the **FULL current DSL** in `current_dsl` — not a delta or partial snippet.
- `export_high_resolution` expects `input_file` pointing to a `.tex` or `.pdf` file path — not raw DSL text.
- `language="zh"` requires XeLaTeX installed on the system; run `doctor` first to verify availability.
- `auto_purpose=true` may override explicit `tree_layout` settings — use one or the other, not both.
- `assess_quality_enhanced` accepts an optional `theme` parameter; pass the same theme used in generation for accurate scoring.
- `apply_purpose_template` requires `template_id` (not `purpose`) since tikz-writer v1.1.0+. If you get an 'unknown parameter' error, verify your tikz-writer version with `doctor`.

## CLI Fallback Reference

When MCP tools silently ignore advanced parameters (e.g., `cycle_removal`, `coord_assignment`) or return errors on unrecognized parameters, fall back to the tikz-writer CLI which supports the full parameter set natively.

### CLI Entry Point

```
/home/gw/opt/tikz_writer/.venv/bin/diagram <subcommand>
```

Path varies by installation. Probe with `which diagram` first; if not on PATH, use the absolute path above.

### Core Subcommands

| Subcommand | Purpose | MCP Equivalent |
|------------|---------|----------------|
| `render` | Render DSL → TikZ/PDF/PNG/SVG | `generate_diagram` |
| `nl` | Natural language → DSL | `generate_diagram` (with `content_type="natural_language"`) |
| `nl-patch` | NL-driven DSL modification | `modify_diagram` |
| `doctor` | Environment diagnostics | `doctor` |
| `theme list` | List available themes | `list_themes` |

### MCP → CLI Parameter Mapping (`render` subcommand)

| MCP Parameter | CLI Flag | Values |
|---------------|----------|--------|
| `cycle_removal` | `--cycle-removal` | `simple`, `dfs_back`, `none` |
| `layer_assignment` | `--layer-assignment` | `bfs`, `longest_path` |
| `coord_assignment` | `--coord-assignment` | `parents_bary`, `sequential`, `children_bary` |
| `layout_mode` | `--layout-mode` | `standard`, `compact` |
| `tree_layout` | `--tree-layout` | `auto`, `off`, `tidy` |
| `tree_child_order` | `--tree-child-order` | `id`, `label` |
| `seed` | `--seed` | integer |
| `aspect_ratio` | `--aspect-ratio` | e.g. `16:9`, `4:3`, float |
| `aspect_mode` | `--aspect-mode` | `fit`, `fill`, `none` |
| `language` | `--language` | `en`, `zh` |
| `nudge_overlaps` | `--nudge` / `--no-nudge` | boolean |
| `no_legend` | `--no-legend` | flag |
| `strict` | `--strict` | flag |

### Fallback Trigger Conditions

1. MCP tool returns an **unrecognized parameter** error for a supported layout option.
2. MCP tool returns **success** but the output `.tex` does not reflect the requested parameter effect (e.g., `cycle_removal="dfs_back"` was set but back-edges are still rendered as normal edges).

### Example CLI Invocation

```bash
# Write DSL to temp file, render with cycle removal
cat > /tmp/tikz-writer-cli/input.dsl << 'EOF'
<DSL content>
EOF

/home/gw/opt/tikz_writer/.venv/bin/diagram render \
  --dsl /tmp/tikz-writer-cli/input.dsl \
  --cycle-removal dfs_back \
  --seed 42 \
  --pdf \
  --format png \
  --out-dir /tmp/tikz-writer-cli/output
```
