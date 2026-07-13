---
name: fst-journal
description: "Fusion Science and Technology (FST) journal submission skill pack — ANS format, single-column, page limits, double-blind optional, data availability statement. Use when: preparing a manuscript for FST (ANS) submission. FST 期刊投稿包：ANS 格式、页数限制、双盲可选、数据可用性声明。"
revision: 1
---

# Fusion Science and Technology (FST) — Journal Submission Pack

## Journal Overview

- **Publisher**: American Nuclear Society (ANS) / Taylor & Francis
- **ISSN**: 1536-1055 (print), 1943-7641 (online)
- **Scope**: Fusion science, plasma engineering, tritium science and technology, fusion materials, blanket and shielding design, safety and environmental aspects
- **Article types**: Technical papers, technical notes, critical reviews, rapid communications

## Manuscript Format (LaTeX)

FST uses the ANS LaTeX template. Template available from ANS or Overleaf.

```latex
\documentclass{ansarticle}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{siunitx}
```

**Key format requirements:**
- Single-column, double-spaced for review
- Maximum length: ~25 double-spaced pages for technical papers (excluding figures/tables)
- Technical Notes: ~14 pages
- No line numbers required in submission
- Nomenclature section: required for symbols-heavy papers (after abstract)

## Nomenclature Section

```latex
\section*{Nomenclature}
\begin{tabular}{p{2cm} p{12cm}}
$TBR$ & Tritium breeding ratio \\
$\Lambda$ & Neutron multiplication factor \\
$E_{dpa}$ & Displacements per atom damage energy \\
\end{tabular}
```

## Figure Specifications

| Property | Requirement |
|----------|-------------|
| Format | TIFF, EPS, or high-quality JPEG |
| Resolution | 300 dpi minimum; 600 dpi recommended for line art |
| Color | Color accepted (online + print) |
| Figure caption | Below figure, "Fig. 1." format |
| In-text placement | Near first citation |
| Width | Fit within 15 cm (single column) |
| Text in figures | ≥ 2.5 mm height when printed |

## Table Specifications

- Numbered sequentially: TABLE I, TABLE II, ...
- Title above table
- Units in column headers
- Three-line table style preferred
- Footnotes: superscript lowercase letters

## Citation Format

- **Style**: Numbered `1,2`, sequential by first appearance
- **Format**: `1. J. SMITH and M. KIM, "Title," Nucl. Fusion, 65, 012001 (2025); https://doi.org/...`
- **DOI**: Required when available
- **URL**: Required for reports, theses, conference papers without DOI

```bibtex
@article{ref1,
  author  = {Smith, J. and Kim, M.},
  title   = {Neutronics and shielding analysis for the ARC fusion pilot plant},
  journal = {Fusion Science and Technology},
  volume  = {81},
  number  = {3},
  pages   = {234--250},
  year    = {2025},
  doi     = {10.1080/15361055.2025.xxxxx}
}
```

## Double-Blind Review

FST offers double-blind review as an option:
- Remove author names and affiliations from manuscript
- Replace with "Author identities withheld for double-blind review"
- Remove acknowledgments (add after acceptance)
- Self-citations: cite as "Author (2025)" without names in text
- Metadata submitted separately

## Data Availability Statement

Required for all FST submissions. Template:

```
The data that support the findings of this study are available
[from the corresponding author upon reasonable request / in
the supplementary material / at [repository URL]].
```

## Submission Checklist

- [ ] Manuscript: `.tex` + `.pdf` or `.docx`
- [ ] Cover Letter
- [ ] Nomenclature section (if symbols-heavy)
- [ ] Data Availability Statement
- [ ] ORCID IDs for all authors
- [ ] CRediT author contributions
- [ ] Conflict of Interest declaration
- [ ] Figure permissions (if reproducing figures from other sources)
- [ ] Supplementary material (if applicable)

## Agent Integration

- Use `academic-writer` agent for FST formatting
- Use `doublecheck` agent for self-citation compliance in double-blind mode
- Use `structure-format-scanner` for nomenclature completeness check
- Use `literature-manager` for DOI verification on all citations

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-07-13 | Initial creation — adapted from ANS/Taylor & Francis FST author guidelines | Agent science capability upgrade plan |
