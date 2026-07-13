---
name: mlst-journal
description: "Machine Learning: Science and Technology (MLST) journal submission skill pack — IOP open access, multidisciplinary ML journal, IOP LaTeX template, 300-word abstract, figures at ≥300 dpi, Vancouver or Harvard referencing, code/data supplementary. Use when: preparing an ML-for-science manuscript for MLST (IOP). MLST 期刊投稿包：IOP OA期刊、多学科ML、LaTeX模板、代码/数据补充材料。"
revision: 1
---

# Machine Learning: Science and Technology (MLST) — Journal Submission Pack

## Journal Overview

- **Publisher**: IOP Publishing (Open Access)
- **ISSN**: 2632-2153
- **Scope**: Multidisciplinary journal bridging ML applications across sciences with advances in ML methods motivated by physical insights
- **Impact Factor**: 4.2 (Citescore: 6.7)
- **Review timeline**: median 5 days to first decision (pre-review), 52 days to first decision (post-review)
- **Article types**: Research papers, reviews, focus collection articles
- **Open Access**: Gold OA — APC applies (check current rates)

## What MLST Looks For

> Articles are expected to **either**:
> i) Make conceptual or methodological advances in ML **with applications to (or motivated by) scientific problems**
> ii) Advance the state-of-the-art of **ML-driven applications in the sciences**

This means pure ML theory without scientific application, or pure science without ML novelty, are both out of scope. The key differentiator from pure ML journals (JMLR, NeurIPS) is the **science connection**.

## Manuscript Format (LaTeX)

Uses the standard IOP LaTeX template (`iopart.cls`).

```latex
\documentclass[12pt]{iopart}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{siunitx}
\usepackage{amsmath}
\usepackage{hyperref}

\begin{document}
\title{Title of your ML-for-science paper}
\author{Author One$^1$, Author Two$^{2,*}$}
\address{$^1$ Institution, City, Country}
\address{$^2$ Institution, City, Country}
\ead{corresponding@email.edu}
\begin{abstract}
...
\end{abstract}
\keywords{keyword1, keyword2, keyword3}
\maketitle
...
\end{document}
```

**Key format requirements:**
- Single-column throughout (IOP standard)
- No need to match published layout — IOP does typesetting
- Minimum 12pt font, reasonable line spacing for review
- Single PDF for submission (figures and tables embedded in text)
- **No line numbers** required (added automatically on submission)

## Article Structure

Standard IMRaD format expected:

1. **Title** — concise, informative, with key terms for discoverability
2. **Author list** — full names + affiliations + ORCID
3. **Keywords** — supplied at submission, used for indexing
4. **Abstract** — ≤300 words, must include: methodology, main results, conclusions. Self-contained (no undefined acronyms, no citations)
5. **Introduction** — problem background, prior work context
6. **Method** — sufficient detail for reproducibility
7. **Results** — main findings, tables and figures
8. **Discussion** — significance, comparison with prior work
9. **Conclusion** — novelty, significance, future work
10. **Acknowledgments** — funding, author contributions (CRediT recommended), conflict of interest
11. **References** — Vancouver [1] or Harvard (Author, Year)

## Figure Specifications

| Property | Requirement |
|----------|-------------|
| Format | Vector EPS or PDF preferred; TIFF/PNG/JPEG accepted |
| Resolution | ≥300 dpi (600 dpi for line art) |
| Color | Full color accepted (no extra charge — all OA) |
| Figure caption | Below figure, self-contained (reader should understand without text) |
| Width | Small/single-column: 8.5 cm; Large/double-column: 15 cm |
| Font in figures | 8–12 pt at final size |
| Multi-panel | (a), (b), (c) labels with combined caption |
| Permissions | Required for reproduced figures from other publishers |

**Accessibility note:** Avoid color as the ONLY means of conveying information. Use different line styles, symbols, or labels alongside color.

## Table Specifications

- Numbered sequentially: Table 1, Table 2, etc.
- Caption above table, concise
- No colored text or shading — use bold/italics for emphasis
- Gridlines: IOP style (three-line preferred)

## Citation Format

MLST accepts **either** Vancouver numbered or Harvard author-year:

### Vancouver (Recommended)

`[1] Author A, Author B and Author C 2025 Mach. Learn.: Sci. Technol. 6 012001`

```bibtex
@article{ref1,
  author  = {Smith, J. and Kim, M. and Mueller, D.},
  title   = {Graph neural networks for fusion plasma control},
  journal = {Machine Learning: Science and Technology},
  volume  = {6},
  pages   = {012001},
  year    = {2025},
  doi     = {10.1088/2632-2153/xxxxx}
}
```

### Harvard (Alternative)

`(Smith et al 2025)` with alphabetical reference list.

## Code, Data & Supplementary Material

MLST **strongly encourages** code and data sharing:
- **Supplementary material**: Submit alongside article (≤50 MB per file, ≤150 MB total)
- **Code repositories**: Link to GitHub/Zenodo with DOI preferred
- **Datasets**: Deposit in field-specific repositories with DOI
- Each supplementary file requires a title (≤30 chars) and description (≤30 words)

### Supplementary File Template

```
Title:  "Supplementary training curves"
Description:  "Training and validation loss curves for all 12 model variants across 200 epochs"
```

## Submission Checklist

- [ ] Manuscript: single PDF with embedded figures and tables
- [ ] Abstract ≤300 words, self-contained
- [ ] Keywords provided
- [ ] All authors have ORCID (recommended)
- [ ] Funding sources declared in acknowledgments
- [ ] CRediT author contribution statement (recommended)
- [ ] Conflict of interest disclosed
- [ ] Code repository link (highly recommended)
- [ ] Data availability statement
- [ ] Supplementary files with title + description (if applicable)
- [ ] Figure permissions (if reproducing from other sources)
- [ ] APC funding confirmed (Gold OA journal)

## MLST vs Other ML Journals

| Factor | MLST | NeurIPS/ICML/JMLR | Nuclear Fusion | FED |
|--------|------|-------------------|----------------|-----|
| ML novelty required | Yes (but can be application-driven) | Yes (strongly) | No | No |
| Science domain required | Yes | No | Fusion only | Fusion eng. |
| OA | Gold OA (APC) | Mixed | Hybrid | Hybrid |
| Figure format | EPS/PDF preferred | Any | EPS/PDF | TIFF/EPS/PDF |
| Abstract length | 300 words | Varies | 200 words | 200 words |

## Special Focus Collections

MLST regularly runs Focus Collections aligned with workshops and emerging topics. Relevant current collections for nuclear engineering ML:
- **Focus on AI Scientists and Scientific Multi-Agent Systems** — directly relevant to your agent fleet research
- **Focus on Autonomous Experimentation, Robust Infrastructure and Trustworthy Agents**
- **Focus on Physics-Informed Machine Learning**
- **Focus on Machine Learning for Large Scale Facilities**

Check the journal homepage for open calls.

## Useful Commands

```bash
# Compile with IOP template
pdflatex manuscript.tex
bibtex manuscript
pdflatex manuscript.tex
pdflatex manuscript.tex

# Check figure DPI
identify -format "%f: %x x %y\n" fig*.png

# Word count for abstract
detex manuscript.tex | sed -n '/begin{abstract}/,/end{abstract}/p' | wc -w
```

## Agent Integration

- Use `academic-writer` agent for MLST-formatted manuscript (IOP article style)
- Use `scientific-paper-research` agent for Focus Collection topic alignment
- Use `figure-quality-reviewer` for resolution and accessibility compliance
- Use `deep-lint-pipeline` skill for pre-submission quality check
- Use `literature-manager` for DOI verification on all references

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-07-13 | Initial creation — adapted from IOP MLST author guidelines (https://publishingsupport.iopscience.iop.org/journals/machine-learning-science-and-technology/) | Agent science capability upgrade plan |
