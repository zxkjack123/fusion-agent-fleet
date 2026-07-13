---
name: nf-journal
description: "Nuclear Fusion (NF) journal submission skill pack — IOP format, LaTeX template, separate figure files, Keywords ≥3, 200-word abstract. Use when: preparing a manuscript for Nuclear Fusion (IOP) submission. NF 期刊投稿包：IOP 格式、LaTeX 模板、独立图表文件。"
revision: 1
---

# Nuclear Fusion (NF) — Journal Submission Pack

## Journal Overview

- **Publisher**: IOP Publishing (International Atomic Energy Agency)
- **ISSN**: 0029-5515 (print), 1741-4326 (online)
- **Scope**: Magnetic and inertial confinement fusion, plasma physics, fusion technology, reactor concepts
- **Impact**: Top-tier fusion journal; Letters, Papers, Reviews, Special Issue articles

## Manuscript Format (LaTeX)

NF provides an official IOP LaTeX template: `iopart.cls`.

```latex
\documentclass[12pt]{iopart}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{siunitx}
```

**Key format requirements:**
- Single-column layout throughout
- Section numbering: 1, 2, 3 (no subsections deeper than 2 levels without editorial permission)
- Abstract: ≤ 200 words
- PACS codes: optional but recommended
- Keywords: ≥ 3 keywords immediately after PACS

## Figure Specifications

| Property | Requirement |
|----------|-------------|
| Format | EPS or PDF (vector preferred); TIFF/PNG for photos |
| Resolution | 600 dpi for line art; 300 dpi for halftones |
| Color | Online color free; print color may incur charges |
| Figure caption | Below figure, "Figure 1." format |
| Files | Submit as separate files (not embedded in LaTeX) |
| Multi-panel | Combine into single file with (a), (b) labels |
| Width | 8.3 cm (single column) or 17 cm (full page) |
| Font in figures | ≥ 8 pt when scaled to published size |

## Table Specifications

- Use `\begin{table}` with `\caption{}` above
- Three-line table style (`\toprule`, `\midrule`, `\bottomrule`)
- Table notes as `\begin{tablenotes}` with `\item[a]...`
- No vertical rules
- Units in parentheses in column headers

## Citation Format

- **Style**: Vancouver numbered: `[1]`, `[2]`, sequential
- **Format**: `[1] Author A, Author B and Author C 2025 Nucl. Fusion 65 012001`
- **DOI**: Required
- **ArXiv**: Include if preprint

```bibtex
@article{ref1,
  author  = {Smith, J. and Kim, S. and Mueller, D.},
  title   = {Neutronics analysis of the DEMO HCCB blanket},
  journal = {Nuclear Fusion},
  volume  = {65},
  pages   = {012001},
  year    = {2025},
  doi     = {10.1088/1741-4326/xxxxx}
}
```

## Manuscript Structure

1. Title (concise, informative, no abbreviations)
2. Author list with affiliations (ORCID recommended)
3. Abstract (≤200 words)
4. Keywords (≥3)
5. Introduction
6. [Methodology sections]
7. Results and Discussion
8. Conclusion
9. Acknowledgments
10. References
11. Figure captions (on separate page in submission)

## Letter Articles

NF Letters:
- ≤ 5 printed pages (~3500 words)
- 3-4 figures maximum
- Urgent or particularly novel results
- Faster review timeline

## Submission Checklist

- [ ] Manuscript: `.tex` + `.pdf` (no `.docx`)
- [ ] Cover Letter with novelty statement and suggested reviewers
- [ ] All figures as separate EPS/PDF files
- [ ] ORCID IDs for all authors (strongly recommended)
- [ ] Data availability statement
- [ ] Author contribution statement
- [ ] Supplementary material (if any, as single PDF)

## Useful Commands

```bash
# Compile with IOP template
pdflatex manuscript.tex
bibtex manuscript
pdflatex manuscript.tex
pdflatex manuscript.tex
```

## Agent Integration

- Use `paper-reviewer` agent for pre-submission peer review simulation
- Use `academic-writer` agent with NF style guidelines
- Use `manuscript-lint` for figure/table numbering checks
- Use `figure-quality-reviewer` for resolution and font-size compliance

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-07-13 | Initial creation — adapted from IOP Nuclear Fusion author guidelines | Agent science capability upgrade plan |
