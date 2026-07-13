---
name: fusion-magnet-heating-normalization
description: Fusion magnet nuclear heating normalization and tally-scope audit for MCNP/OpenMC sector models; 聚变磁体核热归一化、扇区模型、TF/PF线圈、tally覆盖范围、源强换算、Excel交叉校核。
revision: 1
---

# Fusion Magnet Heating Normalization

## When to Use

Use this skill when analyzing or reviewing nuclear heating, dose, or power deposition for fusion magnets in sector-symmetric transport models, especially when results are reported for TF/PF coils, magnet cases, insulation, superconducting coils, or segmented coil regions.

Typical triggers:

- A result is converted from MCNP/OpenMC per-source tallies to kW, W, Gy/s, or W/kg.
- A sector model uses 22.5°, 11.25°, 45°, cyclic symmetry, reflective boundaries, or split magnet geometry.
- A magnet tally covers only `TF1`, `TF2`, one side of a coil, one repeated segment, or selected component cells.
- Reported totals disagree between scripts, spreadsheets, reports, or collaborators.
- Excel formulas include multipliers such as `×2`, `×16`, `×32`, sector source strengths, or empirical toroidal weights.

## When NOT to Use

Do not use this skill for:

- Pure geometry editing with no heating/power normalization.
- Non-magnet component totals unless the same sector/tally-scope ambiguity exists.
- Final safety claims without also running the relevant physical plausibility and uncertainty checks.
- Replacing direct tally-card inspection; this skill tells the agent what to inspect, not what the model contains.

## Workflow

1. **Identify the reported quantity**
   - Record whether the target is `case`, `coil`, `insulation`, `case + coil`, or `case + insulation + coil`.
   - Record units: `MeV/source`, `W`, `kW`, `W/kg`, `Gy/s`, or another dose/power unit.
   - Record whether values are per cell, per segment, per half magnet, per complete magnet, per sector, or full ring.

2. **Inspect tally coverage before applying multipliers**
   - Read tally cards and comments, not just result filenames.
   - List the cell ranges included in each tally.
   - Map cells back to component names such as `TF1`, `TF2`, `PF`, `case`, `coil`, and `insulation`.
   - Decide whether the tally covers one side, both sides, one complete magnet, multiple magnets, or only repeated subsegments.

3. **Separate geometry factors from physics/source factors**
   - Geometry sector factor: e.g. `22.5° → full ring = ×16`.
   - Split-magnet factor: e.g. `TF1 half → complete TF = ×2`.
   - Repetition factor: number of identical sectors, coils, modules, or repeated cells actually represented.
   - Empirical or design margin factor: e.g. toroidal non-uniformity weight `W_toroidal = 1.0` or `1.2`.
   - Do not use an empirical weight to compensate for missing geometry unless explicitly justified.

4. **Reconstruct source normalization explicitly**
   - For DT fusion source normalization, compute or verify source rate from fusion power and energy per reaction.
   - Keep sector source strength separate from total source strength.
   - For MCNP F6/F7-style energy deposition tallies, convert `MeV/source` to watts using source rate and `1.602176634e-13 J/MeV` unless the project defines a specific rounded constant.
   - State whether the tally already includes neutrons, photons, or both.

5. **Audit segmented tallies**
   - Determine whether multiple tally numbers represent independent totals or repeated segment outputs.
   - If `f116-f166`-style tallies each cover the same segmented physical object with different segment grouping, do not sum them as independent magnet totals unless cell coverage proves they are disjoint.
   - Check whether segment sums are expected to be equal, complementary, or diagnostic only.

6. **Cross-check spreadsheets and scripts**
   - Inspect formulas, cached values, labels, and source columns.
   - Interpret formulas like `cell_value × 2 × 16 × source × J_per_MeV / 1000` as a chain of assumptions, not just arithmetic.
   - Verify whether spreadsheet inputs are single-cell values, grouped component sums, or already-normalized totals.
   - Recompute at least one key result independently from raw tally values.

7. **Report every result with a full口径 label**
   - Include component scope, tally scope, geometry factor, source power, optional toroidal weight, and whether uncertainty is acceptable.
   - Example: `TF case + coil, TF1-only ×2×16, 20 MW, no toroidal weight`.
   - Avoid ambiguous labels such as `total TF heating` unless the exact scope is defined nearby.

## Inputs & Outputs

Inputs:

- MCNP/OpenMC input files containing tally cards and component cells.
- Transport output files with energy deposition or heating tallies.
- Parsing scripts, notebooks, or spreadsheet formulas used for post-processing.
- Geometry notes describing sector angle, reflective boundaries, and magnet repetition.

Outputs:

- A normalization audit table with raw tally, source factor, geometry factor, optional weight, and final result.
- A tally coverage statement: e.g. `TF1 only`, `TF1 + TF2`, or `complete magnet already represented`.
- A discrepancy diagnosis if script/spreadsheet/report values disagree.
- Recommended corrected labels or parser outputs.

## Checklist

Before accepting a magnet heating number, verify:

- [ ] The tally cell list maps to the intended magnet components.
- [ ] The tally covers the intended side/half/full magnet scope.
- [ ] Sector-to-full-ring factor is explicit.
- [ ] Split-magnet or reflected-boundary compensation is explicit.
- [ ] Empirical toroidal weight is separate from geometry compensation.
- [ ] Component scope is explicit: `case`, `coil`, `insulation`, or combinations.
- [ ] Segmented tallies are not double-counted.
- [ ] Spreadsheet formulas are traced to raw values and units.
- [ ] Result labels include source power and all multipliers.
- [ ] Relative errors or statistical uncertainty are checked before using small differences.

## BEST Case Pattern

In the BEST divertor shielding audit, a 22.5° MCNP model contained `TF1` and `TF2` halves. The active `f116-f166` TF heating tallies covered `TF1` only. Therefore, collaborator processing that used `TF1 × 2 × 16` was internally consistent for a full-ring complete-TF `case + coil` result. A previous parser/report value used `TF1 × 16 × 1.2` and included insulation, so it had a different scope and could not be directly compared.

This pattern should be treated as a warning example: when a sector model has magnet halves at reflective planes, `×16` may not be enough to reconstruct complete full-ring magnets.

## Common Pitfalls

- Treating `×16` as both sector replication and half-magnet compensation.
- Treating `TF_WEIGHT = 1.2` or another non-uniformity factor as a substitute for missing geometry.
- Comparing `case + coil` against `case + insulation + coil`.
- Summing repeated diagnostic segment tallies as if they were disjoint magnets.
- Mistaking spreadsheet `all cells` single-cell values for component totals.
- Reporting `total TF` without stating whether the tally is `TF1-only`, `TF2-only`, or `TF1+TF2`.
- Ignoring high relative error in low-statistics segment tallies.

## Revision Log

- revision 1: Initial skill extracted from BEST TF nuclear heating normalization audit, including sector/half-magnet factor separation and spreadsheet cross-check workflow.
