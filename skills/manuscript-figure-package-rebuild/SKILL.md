---
name: manuscript-figure-package-rebuild
description: "Manuscript figure unit fix and submission package rebuild — 稿件图表单位修复与投稿包重建, figure regeneration, unit ledger, MSv/h, GSv, mSv, colorbar fix, FormatForge md2docx, md2latex, xelatex compile, LaTeX zip package, self-contained figures. Use when figure colorbar/axis units must be aligned with manuscript text and a submission package (docx/tex/zip) needs rebuilding."
revision: 1
---

# Manuscript Figure & Submission Package Rebuild

## When to Use

- Figure colorbar/axis units are inconsistent with manuscript text or table values (e.g., script uses Sv/h but manuscript says MSv/h).
- A unit ledger CSV or review report identifies figure/table unit mismatches.
- Submission artifacts (docx, tex, zip) need rebuilding after figure or text changes.
- LaTeX compilation needs verification after figure replacement.

Typical triggers:

- "图表的单位和正文不一致，需要修正后重出图、重建投稿包"
- "Regenerate Fig. X–Y per unit ledger and rebuild package"
- "修了绘图脚本后重新生成 docx/tex/zip"

## When NOT to Use

- Only manuscript text edits without figure regeneration — just rerun FormatForge conversion.
- Creating figures from scratch (new data, new plots) — use Data Analyst or Simulation Analyst instead.
- Only validating existing figures without rebuilding (use `view_image` / Pillow checks directly).

## Workflow

### Phase 1: Inspect & Plan

1. **Read unit ledger.** Locate `unit_ledger_fig_tables.csv` or equivalent review artifact listing each figure/table mismatch.
2. **Read plotting scripts.** For each affected figure, read the generation script to identify:
   - Where data is scaled (e.g., `data_sv_h = ... * scale`)
   - Colorbar/axis label strings
   - Tick formatter lambdas
   - Inset/annotation formatting
3. **Read manuscript captions.** Confirm what units the manuscript claims each figure uses.
4. **Decide scaling strategy.** For each figure:
   - Determine target unit (MSv/h, GSv, mSv, etc.)
   - Calculate divisor (`/1e6` for Sv→MSv, `/1e9` for Sv→GSv, `*1e3` for Sv→mSv)
   - Adjust log-scale `vmin/vmax` accordingly

### Phase 2: Patch Scripts

5. **Apply minimal patches** to each plotting script:
   - Scale the plotted data array (e.g., `data_msv_h = data_sv_h / 1e6`)
   - Update colorbar/axis label string
   - Update tick formatter if present
   - Update annotation/inset text formatting
   - Adjust `vmin/vmax` for log color ranges
6. **Update manuscript captions** if the target unit changed from what was previously written (e.g., "kSv" → "GSv").

### Phase 3: Regenerate Figures

7. **Run each plotting script** from the correct working directory:
   ```
   cd <fed_paper_root> && python3 <script_path>
   ```
8. **Synchronize outputs** if the script writes to a different directory than what the manuscript references (e.g., `cp results_dir/fig.png figures_dir/fig.png`).

### Phase 4: Validate Figures

9. **Check file existence and size** (Pillow `Image.open().size`).
10. **Extract PDF text** to confirm unit labels:
    ```
    pdftotext <fig>.pdf - | grep -E 'MSv/h|GSv|mSv|Sv/h|kSv'
    ```
11. **Preview images** (use `view_image` with thumbnail if any dimension > 2000 px).

### Phase 5: Rebuild Submission Package

12. **DOCX rebuild** via FormatForge `convert_markdown_to_docx`:
    - If default config is broken (reference/CSL resolved to directory), supply explicit `reference_doc` and `csl` paths.
    - Set `allow_degraded=true` if pandoc-crossref is unavailable.
    - Warnings about caption style (`Fig.` vs `Figure`) are expected for FED-style manuscripts.
13. **LaTeX rebuild** via FormatForge `convert_markdown_to_latex`:
    - If default template is broken, supply `/tmp/pandoc-default.latex` (from `pandoc --print-default-template=latex`).
    - Supply explicit `csl` path.
14. **Add Unicode compatibility** if xelatex reports `Missing character` for ∼/≈/σ/γ:
    ```latex
    \usepackage{newunicodechar}
    \newunicodechar{∼}{\ensuremath{\sim}}
    \newunicodechar{≈}{\ensuremath{\approx}}
    \newunicodechar{σ}{\ensuremath{\sigma}}
    \newunicodechar{γ}{\ensuremath{\gamma}}
    ```
15. **Build self-contained LaTeX zip:**
    - Read packaged tex, rewrite `includegraphics` paths from `../07_figures_tables/X.png` to `figures/X.png`.
    - Remove `\graphicspath` pointing to absolute path.
    - Copy all referenced figures (PNG + PDF) into `figures/` subdirectory.
    - Write `README.txt` with build instructions.
    - Zip as `manuscript_<name>_latex.zip`.

### Phase 6: Verify Package

16. **Compile packaged LaTeX** in staging directory:
    ```
    cd /tmp/<staging> && xelatex -interaction=nonstopmode -halt-on-error <name>.tex
    ```
    Confirm exit code 0, page count, and no `Missing character` lines.
17. **Verify zip contents** with `unzip -l`.
18. **Check manuscript for stale unit text** residuals:
    ```
    grep -nE 'y-axis is in kSv|µSv|uSv' manuscript.md
    ```

## Inputs & Outputs

**Inputs**
- Manuscript markdown source (`manuscript_*.md`)
- Unit ledger CSV or equivalent mismatch report
- Plotting scripts (Python/matplotlib)
- Raw simulation data read by scripts (meshtal, CSV, etc.)

**Outputs**
- Regenerated figure files (PNG + PDF)
- Updated manuscript source (caption/text fixes)
- `manuscript_*.docx` — Word version
- `manuscript_*.tex` — LaTeX version (standalone, with Unicode compat)
- `manuscript_*_latex.zip` — Self-contained LaTeX submission package

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| FormatForge config resolves reference/CSL/template to a directory | `ValueError: ... is not a file` | Supply explicit paths for `reference_doc`, `csl`, `template` |
| Log-scale `vmin/vmax` not adjusted after unit rescaling | Colorbar shows blank/saturated | Divide old limits by the same factor as the data |
| `MIN_SIGNAL` threshold not rescaled | Ratio map shows spurious values | Scale threshold by the same factor |
| Packaged `.tex` retains absolute `\graphicspath` | Compilation fails on other machines | Strip or replace with `{figures/}` |
| Unicode symbols ∼ ≈ σ γ in body text | `Missing character` warnings, symbols vanish in PDF | Add `newunicodechar` mappings in preamble |
| Figure output dir ≠ manuscript reference dir | Manuscript shows stale figures | Copy/sync after regeneration |
| xelatex timeout in VS Code terminal (>3 min for large docs) | Terminal reports timeout but compile succeeded | Check log file tail for `Output written on` |
| `pandoc --print-default-template=latex` produces minimal template | Pandoc 3.8+ template is short but functional | This is expected; pandoc injects most preamble via variables |

## Revision Log

| Rev | Date | Changes |
|-----|------|---------|
| 1 | 2026-05-13 | Initial crystallization from FED manuscript Fig. 4–7 unit fix + package rebuild session |
