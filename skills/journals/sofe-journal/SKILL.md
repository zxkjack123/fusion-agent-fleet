---
name: sofe-journal
description: "IEEE Symposium on Fusion Engineering (SOFE) proceedings submission pack — IEEE double-column, 6-page limit, PDF compatibility, author affiliation labeling. Use when: preparing a SOFE conference paper. SOFE 会议论文投稿包：IEEE 双栏、6 页限制、PDF 兼容性。"
revision: 1
---

# IEEE SOFE Proceedings — Submission Pack

## Conference Overview

- **Conference**: IEEE Symposium on Fusion Engineering (SOFE)
- **Publisher**: IEEE
- **Scope**: Fusion engineering and technology — magnets, blankets, divertors, heating, diagnostics, remote handling, safety, tritium, materials
- **Venue**: Biennial international conference
- **Proceedings**: Published in IEEE Xplore

## Manuscript Format (LaTeX)

Use IEEE conference template (`IEEEtran.cls`):

```latex
\documentclass[conference]{IEEEtran}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{siunitx}
\usepackage{cite}
```

**Key format requirements:**
- Double-column, single-spaced
- **Page limit**: 6 pages for contributed papers; 8 pages for invited papers
- Author block: full names, affiliations with superscript numbers, email
- Abstract: ≤ 150 words
- Keywords: 3-5 IEEE keywords
- No page numbers (IEEE adds them)

## Figure Specifications

| Property | Requirement |
|----------|-------------|
| Format | PDF (preferred), EPS, PNG, JPEG |
| Resolution | 300 dpi minimum |
| Color | Full color accepted (no extra charge) |
| Figure caption | Below figure, "Fig. 1." format |
| Width | Single column: 3.5 in (8.9 cm); Double column: 7 in (17.8 cm) |
| Font in figures | ≥ 8 pt when published |

**Critical: IEEE PDF Compliance**

All figures must pass IEEE PDF eXpress validation:
- Font embedding: all fonts must be embedded or subset-embedded
- No Type 3 (bitmap) fonts
- PDF version: ≤ 1.7
- No bookmarks or links in the PDF

```bash
# Check font embedding
pdffonts manuscript.pdf

# Common fix: force font embedding with dvips + ps2pdf
latex manuscript.tex
dvips -Ppdf -G0 -t letter manuscript.dvi
ps2pdf -dPDFSETTINGS=/prepress -dEmbedAllFonts=true manuscript.ps
```

## Table Specifications

- IEEE table style: open (no vertical lines)
- Title above table: "TABLE I" (Roman numerals, small caps)
- Table notes below as superscript letters
- Width: fit single or double column

## Citation Format

- **Style**: IEEE numbered `[1]`, `[2]`
- **Format**: `[1] J. Smith and M. Kim, "Tritium breeding optimization for HCCB blankets," in Proc. IEEE Symp. Fusion Eng. (SOFE), 2025, pp. 1-6.`
- **URL/DOI**: Include when available

```bibtex
@inproceedings{ref1,
  author    = {Smith, J. and Kim, M.},
  title     = {Neutronics optimization of the EU-DEMO tritium breeding blanket},
  booktitle = {Proc. 32nd IEEE Symp. Fusion Engineering (SOFE)},
  year      = {2026},
  pages     = {1--6},
  doi       = {10.1109/SOFE.2026.xxxxx}
}
```

## Author Block Format

```
\author{\IEEEauthorblockN{John Smith\IEEEauthorrefmark{1},
    Minjun Kim\IEEEauthorrefmark{2}}
\IEEEauthorblockA{\IEEEauthorrefmark{1}Institute of Plasma Physics,
    Chinese Academy of Sciences, Hefei, China\\
    Email: j.smith@ipp.ac.cn}
\IEEEauthorblockA{\IEEEauthorrefmark{2}Karlsruhe Institute of Technology,
    Karlsruhe, Germany}}
```

## 6-Page Layout Strategy

To fit within 6 pages:
1. Abstract: ≤ 150 words (saves ~0.3 pages)
2. Figures: 4-6 total, each ≤ single-column width
3. Introduction: 0.5-0.75 pages
4. Methodology: 1-1.5 pages
5. Results: 2-2.5 pages (largest section)
6. Conclusion: 0.25-0.5 pages
7. References: 10-15 entries (0.5 pages)
8. Use `\balance` before references for equal column height on last page

## Submission Checklist

- [ ] Manuscript PDF: IEEE Xplore-compliant (all fonts embedded)
- [ ] Copyright form: signed and submitted
- [ ] Page limit: ≤ 6 pages (contributed) or ≤ 8 pages (invited)
- [ ] Author list matches copyright form
- [ ] All figures at ≥ 300 dpi
- [ ] No page numbers or headers
- [ ] No hyperlinks in the PDF

## Agent Integration

- Use `presentation-architect` for the SOFE oral presentation
- Use `academic-writer` for SOFE manuscript drafting with IEEE constraints
- Use `figure-quality-reviewer` for DPI and font embedding checks

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-07-13 | Initial creation — adapted from IEEE conference proceedings guidelines | Agent science capability upgrade plan |
