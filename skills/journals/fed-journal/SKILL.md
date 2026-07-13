---
name: fed-journal
description: "Fusion Engineering and Design (FED) journal submission skill pack — Elsevier format, double-column optional, figure embedding, Cover Letter requirements. Use when: preparing a manuscript for FED submission. FED 期刊投稿包：Elsevier 格式、图表规范、Cover Letter 要求。"
revision: 1
---

# Fusion Engineering and Design (FED) — Journal Submission Pack

## Journal Overview

- **Publisher**: Elsevier
- **ISSN**: 0920-3796
- **Scope**: Fusion engineering, blanket/first-wall/divertor design, tritium systems, remote handling, safety, materials, magnets, heating systems, diagnostics
- **Article types**: Research papers, reviews, technical notes, short communications

## Manuscript Format (LaTeX)

FED uses the standard Elsevier LaTeX template (`elsarticle.cls`).

```latex
\documentclass[review]{elsarticle}  % or [final] for submission
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{siunitx}
\journal{Fusion Engineering and Design}
```

**Key format requirements:**
- Double-column layout optional (single-column acceptable for review)
- Section numbering: 1, 1.1, 1.1.1 (Arabic numerals)
- Abstract: 200 words maximum
- Keywords: 3-6 keywords immediately after abstract
- Highlights: 3-5 bullet points (85 characters each, submitted separately)

## Figure Specifications

| Property | Requirement |
|----------|-------------|
| Format | TIFF, EPS, PDF (vector preferred) |
| Resolution | 300 dpi minimum for halftones; 500 dpi for line art |
| Color | Color figures free online; check print charges |
| Figure caption | Below figure, "Fig. 1." format |
| Embedded in text | Allowed during review; separate files for final submission |
| Multi-panel | Use (a), (b), (c) labels; combine into single file |
| Width | Single column: 90 mm; Double column: 190 mm |

## Table Specifications

- Use `booktabs` package: `\toprule`, `\midrule`, `\bottomrule`
- No vertical lines
- Table caption above: "Table 1" format
- Units in column headers, not repeated in cells
- Footnotes: superscript lowercase letters

## Citation Format

- **Style**: Numbered `[1]`, `[2]`, sequential by first appearance
- **Format**: `[1] A.B. Author, C.D. Author, Title, Journal Volume (Year) Pages.`
- **DOI**: Required when available
- **Self-citation**: Transparent but not excessive

```bibtex
@article{ref1,
  author  = {Smith, J. and Jones, M.},
  title   = {TBR optimization for HCCB blanket},
  journal = {Fusion Engineering and Design},
  volume  = {123},
  pages   = {456--470},
  year    = {2025},
  doi     = {10.1016/j.fusengdes.2025.xxxxx}
}
```

## Submission Checklist

- [ ] Manuscript: `.tex` + `.pdf` or `.docx`
- [ ] Cover Letter (required): explain significance, declare no prior publication
- [ ] Highlights: 3-5 bullet points (85 chars max each)
- [ ] Graphical Abstract: optional but recommended (PNG, 531×1328 px max)
- [ ] Declaration of Competing Interests
- [ ] Author contributions (CRediT format)
- [ ] Data Availability Statement
- [ ] Supplementary material: separate file(s)

## Cover Letter Template

```
Dear Editor,

I/We submit the manuscript titled "[TITLE]" for consideration in
Fusion Engineering and Design.

[2-3 sentences on significance and novelty]

This work has not been published previously and is not under
consideration elsewhere. All authors have approved the manuscript.

Suggested reviewers: [optional, 3-5 names with affiliations]

Sincerely,
[Corresponding Author]
```

## Useful Commands

```bash
# Compile with elsarticle
pdflatex manuscript.tex
bibtex manuscript
pdflatex manuscript.tex
pdflatex manuscript.tex

# Check figure resolution
identify -format "%f: %wx%h\n" fig*.tiff

# Word count for abstract
detex manuscript.tex | grep -A1 "begin{abstract}" | wc -w
```

## Agent Integration

- Use `academic-writer` agent for manuscript drafting with FED style
- Use `format-engineer` agent for LaTeX → DOCX conversion if needed
- Use `deep-lint-pipeline` skill for pre-submission quality check
- Use `manuscript-figure-package-rebuild` skill for figure unit/size alignment

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-07-13 | Initial creation — adapted from Elsevier FED author guidelines | Agent science capability upgrade plan |
