---
description: "OpenMC Monte Carlo transport code: Python API modeling rules, source/tally configuration, common pitfalls, and validation checklist"
applyTo: "simulation-builder,simulation-analyst,fusion-deep-research"
revision: 2
---

> **Companion tools**: 输入语法/类型校验由 `openmc-validator-mcp` (Repo B) 提供 (link TBD)。
> 本 instruction 只覆盖 **物理约定与文化惯例**（单位、能群方向、命名规范），
> 不涉及语法校验 — agent 构建完输入后必须通过 MCP 工具校验再提交 HPC。

# OpenMC — Input Format & Validation Reference

Applicable versions: OpenMC ≥ 0.14.0 (Python API). Note version-specific differences where marked.

## INPUT FORMAT

### Model Construction Sequence

OpenMC models are built via the Python API in this canonical order:

1. **Materials** — `openmc.Material()`, set nuclide composition, density, temperature
2. **Geometry** — `openmc.Cell()`, `openmc.Universe()`, `openmc.Geometry()`; or DAGMC integration (see `instructions/dagmc.instructions.md`)
3. **Settings** — `openmc.Settings()`: `batches`, `inactive`, `particles`, source definition, run mode
4. **Tallies** — `openmc.Tally()` with filters/scores; `openmc.Tallies()` collection

Export via `model.export_to_model_xml()` or run directly via `openmc.run()`.

### Energy Filter Convention

`openmc.EnergyFilter(bins)` — energy bin boundaries in **ascending order** (eV). Example:

```python
# 4-group structure: thermal / epithermal / fast / high-energy
energy_bins = [0.0, 0.625, 1e5, 2e7, 2.5e7]  # ascending, 5 boundaries → 4 groups
ef = openmc.EnergyFilter(energy_bins)
```

**CRITICAL**: This is **opposite** to FISPACT-II's descending convention. When transferring spectra from OpenMC to FISPACT-II, reverse the group order and convert bin boundaries to bin-integrated flux values.

### Cross-Section Library Configuration

- Environment variable: `OPENMC_CROSS_SECTIONS` → path to `cross_sections.xml`
- In Python: `openmc.config['cross_sections'] = '/path/to/cross_sections.xml'`
- Temperature interpolation: set `openmc.Settings().temperature` dict (`method`, `tolerance`, `multipole`)
- Common libraries: ENDF/B-VIII.0, ENDF/B-VII.1, JEFF-3.3, TENDL-2019

### Source Definition

- **Point/spatial sources**: `openmc.IndependentSource(space=..., energy=..., angle=...)`
- **Energy distributions**:
  - Watt fission spectrum: `openmc.stats.Watt(a=0.988e6, b=2.249e-6)` (U-235 thermal fission)
  - D-T fusion: `openmc.stats.Muir(e0=14.08e6, m_rat=5.0, kt=20000.0)` or `openmc.stats.Discrete([14.1e6], [1.0])`
  - Tabular: `openmc.stats.Tabular(x, p, interpolation='histogram')` — x in eV ascending
- **MeshSource** (v0.14+): for spatially-distributed sources from coupled calculations
- Always verify source energy range covers the physics scenario (D-T: peak at 14.1 MeV, fission: up to ~20 MeV)

### Depletion

- Requires a depletion chain file: `openmc.deplete.Chain.from_xml('/path/to/chain.xml')`
- Common chains: `chain_endfb71_pwr.xml`, `chain_endfb80.xml`
- Operator: `openmc.deplete.CoupledOperator(model, chain_file, ...)`
- Time steps and power/flux: `integrator = openmc.deplete.CECMIntegrator(operator, timesteps, power=...)`

## COMMON PITFALLS

### P1: Missing or Incorrect Batch Settings
**Symptom**: keff does not converge; results have large variance.
**Cause**: `inactive` batches set too low (or zero) for eigenvalue problems; total `batches` insufficient for statistical convergence.
**Prevention**: For keff calculations, use ≥50 inactive batches and ≥200 active batches as starting point. Check Shannon entropy convergence.

### P2: Tally Trigger Infinite Loop
**Symptom**: Simulation runs indefinitely, never terminates.
**Cause**: `tally.triggers` with unreachable relative error target (e.g., `rel_err < 0.001` on a rare reaction).
**Prevention**: Set a `Settings.trigger_max_batches` limit. Start with relaxed triggers and tighten after confirming feasibility.

### P3: Depletion Chain File Not Specified
**Symptom**: `RuntimeError` or missing isotopes in depletion results.
**Cause**: Running depletion without specifying a chain file, or using a chain that lacks key isotopes.
**Prevention**: Always explicitly set `chain_file` parameter. Verify key isotopes in the chain (e.g., ⁶Li for TBR, relevant fission products).

### P4: Statepoint I/O Bottleneck
**Symptom**: Simulation slows dramatically at statepoint output intervals.
**Cause**: Large mesh tallies generate multi-GB statepoint files; default writes at every batch.
**Prevention**: Set `Settings.statepoint = {'batches': [final_batch]}` to write only at end, or at sparse intervals. Use `summary.h5` for geometry-only metadata.

### P5: EnergyFilter Boundary Mismatch
**Symptom**: Tally results have unexpected zero bins or integrated value doesn't match total.
**Cause**: Energy bin boundaries don't cover the full source energy range, or bin edges create unintended gaps.
**Prevention**: Ensure lowest bin starts at 0.0 eV (or 1e-5 eV) and upper bin covers source maximum energy. Sum of group tallies should ≈ total tally.

## VALIDATION CHECKLIST

After running OpenMC, verify:

- [ ] **keff convergence** (eigenvalue mode): Check Shannon entropy is converged during inactive batches. Final keff uncertainty should be within target (typically <100 pcm for design calculations).
- [ ] **Leakage rate**: For shielding/blanket models, verify leakage fraction is physically reasonable. Zero leakage in a non-reflective geometry → boundary condition error. Very high leakage → geometry or source error.
- [ ] **Tally sum consistency**: Integrated energy-dependent tally ≈ energy-integrated tally within statistics.
- [ ] **Source energy**: Verify source particles sample from intended energy distribution (check `tallies.xml` source energy tally if uncertain).
- [ ] **Cross-section temperature**: Verify temperature settings match the physical scenario (room temp 293.6 K vs. operating temp 500-800 K affects resonance absorption).
- [ ] **Statepoint file integrity**: `openmc.StatePoint(path)` loads without errors; tally DataFrames have expected dimensions.
