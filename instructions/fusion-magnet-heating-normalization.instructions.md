---
description: "Fusion magnet nuclear heating normalization gate: tally coverage, sector/full-ring factors, split TF/PF geometry, component scope, toroidal weighting, and spreadsheet/script cross-checks. 聚变磁体核热归一化门禁，TF/PF线圈，扇区模型，半磁体补偿，源强换算，表格校核。"
applyTo: "simulation-builder,simulation-analyst,fusion-deep-research,paper-reviewer,methodology-deep-reviewer,data-analyst"
revision: 1
---

# Fusion Magnet Heating Normalization Gate

## Trigger

Apply this instruction whenever an agent analyzes, builds, reviews, or reports nuclear heating, power deposition, W/kg, or Gy/s results for fusion magnets, including TF/PF coils, magnet cases, insulation, superconducting coils, coil supports, or segmented magnet regions.

This gate is mandatory when any of the following appear:

- MCNP/OpenMC sector models such as 22.5°, 11.25°, 45°, or reflective/cyclic symmetry sectors.
- Tally labels or component names such as `TF1`, `TF2`, `PF`, `coil`, `case`, `insulation`, `magnet`, `winding`, or `superconductor`.
- Post-processing formulas using factors such as `×2`, `×16`, `×32`, sector source strengths, full-ring multipliers, or toroidal weights.
- Disagreement between MCNP/OpenMC output, parser scripts, Excel workbooks, reports, or collaborator statistics.

## Required Skill

Before accepting or publishing a magnet nuclear heating number, use the skill:

- `skills/fusion-magnet-heating-normalization/SKILL.md`

The skill provides the detailed workflow. This instruction defines the mandatory gate conditions.

## Mandatory Checks

An agent must explicitly verify and report the following items:

1. **Tally coverage**
   - Identify which cells are included in the tally.
   - Map those cells to physical components: `TF1`, `TF2`, `PF`, case, coil, insulation, or other magnet subcomponents.
   - State whether the tally covers a half magnet, complete magnet, one segment, multiple segments, or the full represented sector.

2. **Geometry multiplier separation**
   - Separate sector-to-full-ring factors from split-magnet compensation.
   - Example: in a 22.5° model, `×16` is the sector-to-full-ring factor; if the tally covers only one reflected half such as `TF1`, an additional `×2` may be required.
   - Only apply `×2` after confirming the source tally excludes the matching other half.

3. **Source normalization**
   - Record source power, source rate, energy per reaction or particle normalization, and `J/MeV` conversion.
   - State whether the result is based on neutron-only, photon-only, or neutron+photon tallies.

4. **Component口径**
   - State whether the value includes `case`, `coil`, `insulation`, or combinations such as `case + coil` or `case + insulation + coil`.
   - Do not compare two results unless their component scope is aligned or the difference is explicitly explained.

5. **Empirical weight isolation**
   - Keep toroidal non-uniformity or engineering weight factors separate from geometry completion factors.
   - Do not use a weight such as `1.2` as a substitute for a missing half-magnet or missing sector multiplier.

6. **Segmented tally double-counting check**
   - Confirm whether multiple tally numbers are disjoint component sums or repeated/segmented diagnostic outputs.
   - Do not sum repeated segment tallies as independent magnet totals unless cell coverage proves they are disjoint.

7. **Spreadsheet/script cross-check**
   - If spreadsheets or parser scripts are involved, inspect formulas and labels.
   - Determine whether spreadsheet values are raw cell values, component sums, sector-normalized powers, or full-ring totals.
   - Independently recompute at least one representative result from raw tally values.

8. **Result label completeness**
   - Every delivered result must state: component scope, tally scope, geometry multiplier, source power, optional toroidal weight, and uncertainty status.
   - Preferred label pattern: `<component scope>, <tally scope> × <geometry factors>, <source power>, <weight policy>`.

## Blocking Conditions

Do not deliver the result as a final technical conclusion if any of the following remains unresolved:

- The tally cell coverage is unknown.
- The sector/full-ring multiplier is inferred but not verified.
- A half-magnet or reflected-boundary correction may be missing or duplicated.
- The component scope differs between compared values and is not clearly documented.
- A spreadsheet or script formula applies multipliers whose meaning is not traced.
- Relative uncertainty is too high for the claimed comparison and no caveat is provided.

## Required Output Marker

For deliverables involving magnet nuclear heating, append one of:

- `[Fusion Magnet Heating Normalization Gate: PASS]`
- `[Fusion Magnet Heating Normalization Gate: PARTIAL — <reason>]`
- `[Fusion Magnet Heating Normalization Gate: BLOCKED — <reason>]`

A `PARTIAL` marker is acceptable for internal exploratory analysis if the unresolved item is clearly stated. A `BLOCKED` marker is required for final reports when tally coverage or geometry multipliers remain unknown.

## BEST Warning Example

In a BEST 22.5° TF heating audit, `TF1` and `TF2` were two reflected-plane halves of one complete TF magnet. The active `f116-f166` tallies covered `TF1` only. Therefore, `TF1 × 2 × 16` was the correct complete full-ring geometry口径 for TF1-only source data, while `TF1 × 16 × 1.2` was a different口径 and could not be directly compared.
