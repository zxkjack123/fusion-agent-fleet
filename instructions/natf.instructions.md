---
description: "natf R2S activation-transport coupling program: R2S workflow, phtn_src format, common pitfalls, and validation checklist"
applyTo: ""
revision: 1
---

# natf — R2S Workflow & Validation Reference

natf is a user-developed R2S (Rigorous-2-Step) program for coupled neutron activation and photon transport analysis in fusion nuclear engineering.

## R2S WORKFLOW

### Three-Step Process

```
Step 1: Neutron Transport (OpenMC or MCNP)
  → Mesh-based neutron flux distribution
  ↓
Step 2: Activation Calculation (FISPACT-II, per mesh cell)
  → Nuclide inventory & photon source per cell
  ↓
Step 3: Photon Transport (MCNP)
  → Shutdown dose rate (SDR), contact dose, gamma spectra
```

### Step 1 — Neutron Transport

- Run OpenMC or MCNP with a regular mesh tally (typically structured rectangular mesh) to obtain multi-group neutron flux in each mesh cell.
- The mesh must cover the activation region of interest.
- Flux normalization: absolute flux [n/cm²/s] per mesh cell (not per source particle). Apply source strength multiplication if transport code reports per-source-particle values.
- See `instructions/openmc.instructions.md` or `instructions/mcnp6.instructions.md` for transport code specifics.

### Step 2 — Activation (FISPACT-II)

- natf generates FISPACT-II input files for each mesh cell, using the cell's neutron spectrum.
- Energy group structure must match between the transport mesh tally and FISPACT-II's nuclear data library. See `instructions/fispact-ii.instructions.md` §Spectrum Input.
- Irradiation schedule and material composition are typically shared across all mesh cells (same irradiation scenario).
- Output: per-cell nuclide inventory at specified cooling times, including photon emission spectra (gamma lines).

### Step 3 — Photon Transport (phtn_src → MCNP)

- natf generates a `phtn_src` file containing the photon source distribution for MCNP's mesh source sampling.
- MCNP reads `phtn_src` to sample photon source particles from each mesh cell according to the activation-calculated gamma spectrum.

## PHTN_SRC FORMAT — CRITICAL

### Header Flag: Bounding Box

The `phtn_src` file header contains a flag indicating whether bounding box data is provided:

- **Flag = 1** (WITH bounding boxes): Each cell data line includes `xmin xmax ymin ymax zmin zmax` coordinates. MCNP uses these to efficiently sample source particles only within the cell's spatial extent.
- **Flag = 0** (WITHOUT bounding boxes): MCNP falls back to **rejection sampling over the entire geometry**. For small source cells in a large model, this is catastrophically inefficient — sampling acceptance rate may be <0.01%, effectively causing MCNP to hang.

**CRITICAL RULE**: Always set the bounding box flag to `1` and provide valid bounding box coordinates for each mesh cell. This is the most common natf-related failure mode.

### Cell Data Format

Each non-zero source cell has a line:
```
cell_id  source_intensity  xmin xmax ymin ymax zmin zmax  [energy_group_data...]
```

- `source_intensity`: total photon source [photons/s] for the cell
- Bounding box: in cm, matching the mesh cell boundaries from Step 1
- Energy group data: photon spectrum distribution within the cell

## INPUT CONFIGURATION

`[用户补充]` — natf 配置文件完整参数表：
- Mesh definition parameters (origin, dimensions, spacing)
- FISPACT-II template path
- Material assignment mapping
- Cooling time specification
- Output format options

## CLI INTERFACE

`[用户补充]` — natf 命令行接口：
- Command syntax and subcommands
- Key flags/options
- Version-specific changes

## COMMON PITFALLS

### P1: phtn_src Bounding Box Flag = 0 (CRITICAL)
**Symptom**: MCNP photon transport hangs or runs indefinitely with near-zero sampling efficiency.
**Cause**: `phtn_src` header flag set to 0 → MCNP uses rejection sampling over entire geometry for each source particle.
**Prevention**: Always set flag = 1 and provide valid bounding box data. Verify with: `head -1 phtn_src` should show flag value 1.

### P2: Energy Group Mismatch Between Steps 1 and 2
**Symptom**: Activation results inconsistent with neutron flux levels; may be orders of magnitude off.
**Cause**: Neutron transport mesh tally uses a different energy group structure than the FISPACT-II nuclear data library that natf feeds.
**Prevention**: Explicitly specify the same group structure in both the transport mesh tally configuration and the FISPACT-II input template. Cross-check group count and energy boundaries.

### P3: Mesh Resolution Too Coarse
**Symptom**: SDR field appears artificially uniform; hot spots near beam port or penetrations are missed.
**Cause**: Mesh cells too large to resolve spatial gradients in neutron flux.
**Prevention**: Perform a mesh sensitivity study: compare SDR at key points with 2× refinement. If results change >20%, the mesh is too coarse.

### P4: Source Strength Not Applied
**Symptom**: SDR results scale linearly wrong compared to reference.
**Cause**: Neutron flux from transport is per-source-particle, but natf/FISPACT-II expects absolute flux.
**Prevention**: Verify source strength multiplication is applied in the natf configuration or preprocessing step.

## VALIDATION CHECKLIST

After running the full R2S chain, verify:

- [ ] **phtn_src flag**: `head -1 phtn_src` shows bounding box flag = 1.
- [ ] **SDR magnitude**: Shutdown dose rate should be in the expected range for the material/flux/cooling combination. Typical fusion first-wall SDR: ~10–1000 μSv/h at 10⁶ s cooling (material-dependent).
- [ ] **Spatial distribution**: SDR should peak near high-flux regions (first wall, beam ports) and decay with distance/shielding. Uniform SDR in a non-uniform geometry → mesh or source mapping error.
- [ ] **Energy group consistency**: Verify transport mesh tally group count = FISPACT-II ARBI group count.
- [ ] **Source normalization chain**: Source strength [n/s] × transport flux [per source particle] = absolute flux [n/cm²/s] fed to FISPACT-II.
- [ ] **Cooling time sequence**: phtn_src corresponds to the correct cooling time (check FISPACT-II output index).
