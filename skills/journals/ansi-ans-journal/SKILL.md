---
name: ansi-ans-journal
description: "ANS journal series (NT/NSE/FT) submission pack — Nuclear Technology, Nuclear Science and Engineering, Fusion Technology section. ANS LaTeX template, Nomenclature, 300 dpi figures, SI units mandatory. Use when: submitting to any ANS journal. ANS 系列期刊投稿包：ANS LaTeX 模板、Nomenclature 段、SI 单位强制。"
revision: 1
---

# ANS Journal Series — Submission Pack

## Journals Covered

This pack covers all American Nuclear Society (ANS) journals:

| Journal | ISSN | Scope |
|---------|------|-------|
| **Nuclear Technology (NT)** | 0029-5450 | Reactor physics, fuel cycles, thermal hydraulics, materials |
| **Nuclear Science and Engineering (NSE)** | 0029-5639 | Neutron transport, criticality, shielding, nuclear data |
| **Fusion Science and Technology (FST)** | 1536-1055 | (See also `skills/journals/fst-journal/`) |

## Manuscript Format (LaTeX)

ANS provides an official LaTeX template (`ansarticle.cls`):

```latex
\documentclass{ansarticle}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{siunitx}
% SI units are MANDATORY throughout
\DeclareSIUnit\barn{b}
\DeclareSIUnit\eVpercmsq{\eV\per\cm\squared}
```

**Key format requirements:**
- Single-column, double-spaced for review
- Maximum length: ~25 pages (NT/NSE), ~25 pages (FST)
- Nomenclature section: required for symbols-heavy papers
- SI units: mandatory for all physical quantities
- Page numbers: required on all pages

## Nomenclature Section

Required format:

```latex
\section*{NOMENCLATURE}

\begin{tabular}{p{2.5cm} p{1.5cm} p{9cm}}
$k_{\mathrm{eff}}$ & = & effective neutron multiplication factor \\
$\Sigma_a$ & = & macroscopic absorption cross section (cm$^{-1}$) \\
$\phi$ & = & neutron scalar flux (n/cm$^{2}\cdot$s) \\
$TBR$ & = & tritium breeding ratio \\
\end{tabular}
```

All symbols used in equations and text must be defined.

## Figure Specifications

| Property | Requirement |
|----------|-------------|
| Format | TIFF (preferred), EPS, PDF, high-quality JPEG |
| Resolution | ≥ 300 dpi for halftones; ≥ 600 dpi for line art |
| Color | Accepted; no extra charge for online color |
| Figure caption | Below figure, "Fig. 1." format |
| In-text placement | Near first citation; do not collect at end |
| Width | ≤ 15 cm (single column width) |
| Font in figures | ≥ 2.5 mm when printed |

## Table Specifications

- Roman numerals: TABLE I, TABLE II, ...
- Title above table
- Units in column headers (SI)
- Three-line table style
- Table notes as superscript lowercase letters

## Citation Format

- **Style**: Numbered sequential `1,2,3`
- **Format**: `1. J. SMITH, M. KIM, and D. MUELLER, "Neutronics Analysis of the DEMO Blanket," *Nucl. Technol.*, **210**, 3, 456-478 (2025); https://doi.org/10.1080/...`
- **DOI**: Required when available
- **Journal abbreviations**: ANS standard abbreviations required

## SI Units Policy

ANS journals **require** SI units for all physical quantities. Common nuclear engineering exceptions documented:

| Quantity | SI Unit | Common Alternative (Disallowed) |
|----------|---------|-------------------------------|
| Length | m, cm, mm | inch, feet |
| Energy | J, eV | cal, BTU |
| Power | W | hp |
| Pressure | Pa | psi, bar, atm |
| Cross section | m², cm² | barn (must define: 1 b = 10⁻²⁸ m²) |
| Dose | Gy, Sv | rad, rem |
| Temperature | K | °F |

## Submission Checklist

- [ ] Manuscript: `.tex` + `.pdf` (or `.docx` with ANS template)
- [ ] Cover Letter with novelty statement
- [ ] Nomenclature section (all symbols defined)
- [ ] All figures at ≥ 300 dpi (600 dpi for line art)
- [ ] SI units used throughout
- [ ] All references include DOI
- [ ] ORCID IDs for all authors
- [ ] Copyright transfer form
- [ ] Author contribution statement
- [ ] Data availability statement

## Agent Integration

- Use `academic-writer` agent for ANS-formatted manuscript
- Use `standards-navigator` agent for SDC-IC compliance on safety-related content
- Use `manuscript-lint` for units compliance check (SI-only)
- Use `citation-scanner` for DOI verification on all references

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-07-13 | Initial creation — adapted from ANS author guidelines for NT/NSE/FST | Agent science capability upgrade plan |
