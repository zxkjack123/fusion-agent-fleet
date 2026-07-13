---
description: "Figure visual review criteria: structured checklist for evaluating figures/diagrams in manuscripts, patents, reports, and proposals. 图表视觉审查标准, 轴标签检查, 数据可视化评估, 发布适配性, 图文一致性, 子图风格统一."
applyTo: "paper-reviewer,figure-quality-reviewer,patent-writer,proposal-writer,academic-writer"
revision: 1
---

# Figure Visual Review Criteria — 图表视觉审查标准

This instruction defines a structured checklist for visually inspecting figures in manuscripts, patents, reports, and proposals. Each criterion is classified by enforcement level:

- **MUST**: Failure is a 🔴 Major Issue (blocks publication readiness)
- **SHOULD**: Failure is a 🟡 Minor Issue (recommended fix before submission)
- **MAY**: Advisory only (improvement suggestion, not a defect)

## D1: Basic Completeness — 基础完整性

| # | Check | Level | Pass Criterion |
|---|-------|-------|----------------|
| 1.1 | Axis labels present | MUST | Both X and Y axes (or all relevant axes in 3D) have text labels |
| 1.2 | Units on axes | MUST | Quantitative axes display units in parentheses or brackets (e.g., "Energy (MeV)") |
| 1.3 | Legend present (multi-series) | MUST | Figures with ≥2 data series have a legend distinguishing each series |
| 1.4 | Title or caption adequacy | MUST | Figure has a caption that describes what is shown (not just "Figure 3") |
| 1.5 | Tick marks and scale | SHOULD | Tick marks are present, evenly spaced, and numerically labeled |
| 1.6 | Axis range appropriate | SHOULD | Axes do not extend far beyond data range (no excessive whitespace) |
| 1.7 | Grid lines (when helpful) | MAY | Grid lines present for data-dense plots where precise reading is needed |

## D2: Data Representation — 数据表达恰当性

| # | Check | Level | Pass Criterion |
|---|-------|-------|----------------|
| 2.1 | Chart type matches data | MUST | Visualization type is appropriate for the data relationship (e.g., scatter for correlation, bar for comparison, line for trends over continuous variable) |
| 2.2 | No misleading truncation | MUST | Y-axis starts at zero for bar charts; or non-zero baseline is explicitly marked and justified |
| 2.3 | Error bars / uncertainty | SHOULD | Quantitative data points show uncertainty representation (error bars, confidence bands, or stated in caption) when uncertainty is available |
| 2.4 | Data density appropriate | SHOULD | Not too sparse (wasting space) nor too dense (overlapping markers unreadable) |
| 2.5 | Trend lines labeled | SHOULD | Fitted curves or trend lines are labeled with the model/equation used |
| 2.6 | Outliers visible | MAY | Outliers are not hidden by axis truncation or overlapping markers |
| 2.7 | Colorbar for heatmaps | MUST | Color-mapped plots include a colorbar with label and units |

## D3: Publication Adaptability — 发布适配性

| # | Check | Level | Pass Criterion |
|---|-------|-------|----------------|
| 3.1 | Text legibility at print size | MUST | All text in the figure is ≥8 pt when printed at single-column width (~8 cm / 3.3 in) |
| 3.2 | Grayscale distinguishability | SHOULD | Data series remain distinguishable when converted to grayscale (use both color AND marker/line style) |
| 3.3 | Resolution adequate | MUST | Raster images are ≥300 DPI at print size; vector formats preferred for line art |
| 3.4 | No compression artifacts | MUST | No visible JPEG blocking, ringing, or blurring on text/lines |
| 3.5 | Aspect ratio reasonable | SHOULD | Figure is not excessively stretched or compressed; data aspect ratio matches physical meaning |
| 3.6 | White space balanced | MAY | Margins around plot area are consistent and not excessive |
| 3.7 | Color-blind safe palette | SHOULD | Color scheme avoids red-green only differentiation; uses colorblind-friendly palettes (e.g., viridis, cividis) |

## D4: Consistency — 一致性

| # | Check | Level | Pass Criterion |
|---|-------|-------|----------------|
| 4.1 | Font consistent across figures | SHOULD | Same font family and size scheme used across all figures in the document |
| 4.2 | Color scheme consistent | SHOULD | Same variable uses the same color across different figures |
| 4.3 | Sub-figure style unified | MUST | Multi-panel figures use consistent axis ranges, labels, and styling for comparable panels |
| 4.4 | Symbol/marker consistency | SHOULD | Same data series uses the same marker shape across figures |
| 4.5 | Terminology alignment | MUST | Labels and terms in figures match those used in the main text exactly (no abbreviation drift) |
| 4.6 | Numbering sequential | MUST | Figure numbers are sequential with no gaps or duplicates (cross-check with Structure-Format Scanner D2) |

## D5: Figure-Text Alignment — 图文一致性

| # | Check | Level | Pass Criterion |
|---|-------|-------|----------------|
| 5.1 | Data matches text claims | MUST | Quantitative values cited in the text (e.g., "peak at 14.1 MeV") are visually consistent with the corresponding figure |
| 5.2 | Trends match narrative | MUST | Described trends (e.g., "monotonically increasing") are visually confirmed in the figure |
| 5.3 | Caption matches content | MUST | Caption description matches what is actually displayed (correct variable names, conditions, units) |
| 5.4 | In-text reference correct | SHOULD | "As shown in Fig. X" correctly points to the figure that shows the described content |
| 5.5 | All figures referenced | MUST | Every figure is referenced at least once in the body text (no orphan figures) |
| 5.6 | Annotations consistent | SHOULD | Arrows, labels, or callouts in the figure match the discussion in the text |

## Scoring (for Figure Quality Reviewer output)

For each figure, assign a composite rating:

| Rating | Criteria |
|--------|----------|
| ✅ PASS | Zero MUST failures, ≤2 SHOULD failures |
| ⚠️ NEEDS REVISION | 1 MUST failure OR ≥3 SHOULD failures |
| ❌ UNACCEPTABLE | ≥2 MUST failures |

## Special Cases

### Schematic / Flowchart / Mechanism Diagrams

For non-data figures (apparatus schematics, process flowcharts, mechanism illustrations):
- D2 (Data Representation) checks do not apply
- Replace with: clarity of flow direction, completeness of labeled components, logical grouping, arrow consistency

### Patent Drawings

For patent figures (附图):
- D3.7 (color-blind safe) becomes MAY (patent drawings are typically B&W line art)
- Add: reference numeral consistency with specification text (every numeral in drawing must appear in description and vice versa)

### Photographs / Micrographs

For experimental photographs or microscopy images:
- D1.1/1.2 become: scale bar present with units
- D3.3: original resolution metadata should be stated in caption
- Add: contrast and brightness sufficient to distinguish features described in text
