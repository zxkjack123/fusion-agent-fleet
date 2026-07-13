---
name: figure-style-migration
description: "Figure style migration for nuclear engineering papers — extract visual style from target journal/reference figure (via vision MCP), replicate style with tikz-writer or paperbanana. Use when: adapting figures to match a specific journal aesthetic, replicating an existing figure style for consistency across a paper. 图表风格迁移：从目标期刊/参考图表中提取视觉风格并复现。"
revision: 1
---

# Figure Style Migration

## When to Use

- Adapting a figure to match a specific journal's aesthetic (FED, NF, FST, SOFE, ANS)
- Replicating the visual style of an existing published figure for consistency across a paper
- Migrating a matplotlib figure to a TikZ version matching the target journal style
- Generating new figures that look "like" a reference set of existing figures
- Batch-style migration across all figures in a manuscript

## When NOT to Use

- For creating entirely new figures without a style target — use `tikz-writer` or PaperBanana directly
- For journal format compliance (margins, font, template) — use the relevant `skills/journals/<journal>/SKILL.md`
- For figure content correctness — use `figure-quality-reviewer` agent

## Workflow

### Stage A: Style Extraction

1. **Identify target source**:
   - **Option 1: Reference figure** — a published figure from the target journal whose style you want to replicate
   - **Option 2: Journal corpus** — 3-5 figures from the target journal to extract the "house style"
   - **Option 3: Style guide** — a written style specification (color palette, font, layout preferences)

2. **Extract style features via vision MCP**:
   ```
   vision_query(image_source="reference_figure.png",
     prompt="Analyze the visual style of this scientific figure. Report:
     1. Color palette (list hex codes of all distinct colors used)
     2. Font family and size for axis labels, titles, legend
     3. Line styles (marker shapes, line widths, dash patterns)
     4. Grid and axis styling (presence, transparency, tick direction)
     5. Legend position and style (framed/unframed, orientation)
     6. Background and border treatment
     7. Data-to-ink ratio (minimalist vs decorative)
     8. Sub-panel layout pattern if multi-panel")
   ```

   For cross-validation, use `vision_compare` with 2+ providers and take consensus.

3. **Write style specification**:
   Save extracted style as `style_spec.yaml` in the working directory:
   ```yaml
   source: "Fig. 3 from Kim et al. (2024) NF 64 086012"
   colors:
     primary: "#1f77b4"
     secondary: "#ff7f0e"
     tertiary: "#2ca02c"
     background: "#ffffff"
   font:
     family: "Helvetica"
     axis_size: 9
     title_size: 10
     legend_size: 8
   lines:
     width: 1.2
     marker_size: 4
   grid:
     present: true
     alpha: 0.3
     linestyle: "--"
   legend:
     framed: false
     position: "upper right"
   ```

### Stage B: Style Application

4. **Choose generation path**:
   - **Path A: TikZ** (for diagrams, schematics, flowcharts with LaTeX math)
     → Use `tikz-writer/generate_diagram` or `tikz-writer/modify_diagram`
   - **Path B: PaperBanana** (for methodology diagrams, architecture illustrations)
     → Use `paperbanana generate --venue custom` with the extracted style spec
   - **Path C: Matplotlib** (for data-driven plots)
     → Use `matplotlib-seaborn-viz` skill with the extracted rcParams

5. **Verify migration quality**:
   - Use `vision_query` on the generated figure with prompt "Compare this figure's visual style to the reference. Rate similarity on a 1-10 scale for color, typography, layout, and overall feel."
   - If score < 7, iterate with explicit style corrections.

### Stage C: Iteration

6. **Feedback loop**: For each iteration, adjust specific style parameters and re-generate:
   - Color mismatch → update color palette
   - Font mismatch → update `\usepackage` / matplotlib rcParams
   - Spacing mismatch → adjust margins, padding, aspect ratio

## Nuclear Engineering Applications

### Scenario 1: FED Journal Migration
Extract the Elsevier double-column figure style from a published FED paper, apply to your own OpenMC geometry schematic via PaperBanana.

### Scenario 2: NF Article Figure Consistency
Extract the house style from 3 figures in a published NF paper, apply to all figures in your manuscript for visual coherence.

### Scenario 3: Conference to Journal Upgrade
Take an IEEE SOFE conference figure (constrained by 2-column format) and migrate to full-width Nuclear Fusion journal figure style.

## Tools Used

| Tool | When |
|------|------|
| `vision_query` | Extract style from a single reference figure |
| `vision_compare` | Cross-validate style extraction across multiple VLM providers |
| `tikz-writer/generate_diagram` | Generate TikZ figures with custom theme |
| `paperbanana generate` | Generate methodology diagrams with custom venue |
| `paperbanana polish` | Refine an existing figure to match a venue style |

## Integration with Other Skills

- **skills/journals/*/SKILL.md**: Journal-specific format requirements complement the visual style migration
- **matplotlib-seaborn-viz**: Apply extracted matplotlib rcParams for data plots
- **manuscript-figure-package-rebuild**: Rebuild entire figure set with migrated styles

## Best Practices

1. Extract from 3-5 reference figures for a robust "house style," not just one
2. Use `vision_compare` for critical style extractions (cross-provider validation)
3. Save extracted style specs for reuse across papers targeting the same journal
4. Don't copy the reference figure's content — only its visual styling

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-07-13 | Initial creation — inspired by FigMirror (VILA-Lab) style migration concept, adapted for nuclear engineering paper workflow | Agent science capability upgrade plan |
