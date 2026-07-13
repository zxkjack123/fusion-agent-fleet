---
description: "Multi-code interface contracts: data flow specifications between OpenMC, MCNP6, FISPACT-II, DAGMC, natf, and tricys for coupled nuclear simulation workflows"
applyTo: ""
revision: 1
---

# Multi-Code Interface Contracts — 跨程序接口规范

This document defines the data format, unit, and validation rules for data flowing between nuclear simulation codes in coupled workflows. The primary use case is the **R2S (Rigorous-2-Step) shutdown dose rate** chain, but interfaces also cover other coupling patterns.

## R2S CHAIN OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Neutron Transport         Step 2: Activation           │
│  (OpenMC or MCNP)         →        (FISPACT-II via natf)       │
│                                                                 │
│  Output: mesh neutron flux         Output: per-cell inventory   │
│  [n/cm²/s per group]              & photon source [γ/s]        │
│                                           ↓                     │
│                            Step 3: Photon Transport             │
│                            (MCNP via phtn_src)                  │
│                                                                 │
│                            Output: SDR [μSv/h]                  │
└─────────────────────────────────────────────────────────────────┘
```

## INTERFACE 1: OpenMC → FISPACT-II (Neutron Spectrum Transfer)

### Data Description
Neutron energy spectrum (multi-group flux) from OpenMC mesh tally → FISPACT-II ARBI input block.

### Format Conversion Rules

| Property | OpenMC convention | FISPACT-II convention | Conversion action |
|----------|-------------------|------------------------|-------------------|
| Energy bin order | **Ascending** (low→high) [eV] | **Descending** (high→low) [eV] | **Reverse** the array |
| Energy unit | eV | eV | None |
| Flux value | Per-group integrated flux [n/cm²-source] | Per-group absolute flux [n/cm²/s] | Multiply by source strength [n/s] |
| Group count | Set by EnergyFilter bins | Must match nuclear data library (e.g., 709 for CCFE-709) | Rebin if needed; error if group count mismatch |

### Validation Rules (mandatory before FISPACT-II run)
1. **Group count match**: `len(openmc_flux)` == FISPACT-II ARBI group count == nuclear data library group count.
2. **Energy range coverage**: OpenMC EnergyFilter upper bound ≥ source maximum energy (14.1 MeV for D-T, ≥20 MeV for fission). FISPACT-II ARBI first energy boundary ≥ this value.
3. **Normalization check**: `sum(fispact_flux_groups)` should equal the total scalar flux [n/cm²/s] at the irradiation point. Compare with OpenMC total flux tally (energy-integrated) × source strength.
4. **Non-zero high-energy groups**: For D-T fusion, the 14 MeV group must have non-zero flux. Zero flux in all groups above 10 MeV → spectrum truncation error.
5. **No negative flux values**: Every group flux ≥ 0. Negative values indicate a post-processing error.

### Red Flags (trigger immediate investigation)
- Total flux differs from OpenMC by >10% after normalization → normalization chain error
- Spectrum shape has sharp discontinuity at a group boundary → rebinning artifact
- All flux above 1 MeV is zero in a D-T or fission scenario → **spectrum truncation** (the original incident)

## INTERFACE 2: MCNP → FISPACT-II (Neutron Spectrum Transfer)

### Data Description
MCNP MESHTAL neutron flux → FISPACT-II ARBI input.

### Format Conversion Rules

| Property | MCNP convention | FISPACT-II convention | Conversion action |
|----------|-----------------|------------------------|-------------------|
| Energy bin order | **Ascending** (MeV) | **Descending** (eV) | Reverse AND convert MeV→eV (×1e6) |
| Energy unit | MeV | eV | Multiply boundaries by 1e6 |
| Flux value | Per-source-particle flux | Absolute flux [n/cm²/s] | Multiply by source strength [n/s] |
| Group count | Set by E card bins | Must match library | Rebin if needed |

### Validation Rules
1. **Energy unit conversion**: Verify MeV→eV conversion applied (factor 1e6). Missing conversion → all energies 1e6× too low.
2. **Group count match**: Same as Interface 1.
3. **Normalization**: Same principle as Interface 1 — multiply by source strength.
4. **MESHTAL integrity**: Check MESHTAL header for correct mesh dimensions and tally number.

## INTERFACE 3: FISPACT-II → MCNP (Photon Source via phtn_src)

### Data Description
FISPACT-II per-cell photon emission spectrum → natf → `phtn_src` file → MCNP photon transport.

### Format Rules
- See `instructions/natf.instructions.md` §PHTN_SRC FORMAT for detailed file format.
- Photon source intensity in [photons/s] per mesh cell.
- Photon energy groups: typically 24-group VITAMIN gamma structure or user-defined.
- **Bounding box flag MUST be 1** — see natf instructions §P1.

### Validation Rules
1. **Bounding box present**: `head -1 phtn_src` flag = 1.
2. **Source intensity magnitude**: Total photon source [γ/s] summed over all cells should be physically reasonable for the material activation level. For fusion first-wall steel (1 FPY), expect >1e15 γ/s per m³.
3. **Spatial consistency**: phtn_src mesh dimensions match the original neutron transport mesh (same origin, same cell count, same cell sizes).
4. **Energy group coverage**: Photon spectrum groups should cover the dominant gamma lines for activated materials (typically 0.1–10 MeV).
5. **Cooling time correct**: Verify phtn_src corresponds to the intended cooling step (not shutdown values when 10⁶s cooling is needed, or vice versa).

## INTERFACE 4: OpenMC ↔ DAGMC (Geometry Transfer)

### Data Description
DAGMC .h5m geometry file → OpenMC `DAGMCUniverse`.

### Key Rules
- See `instructions/dagmc.instructions.md` §OpenMC Integration.
- Material name matching: DAGMC group `mat:XXX` must exactly match `openmc.Material.name`.
- Volume IDs: use `auto_geom_ids=True` for automatic ID mapping.

### Validation Rules
1. **Material mapping**: All DAGMC volumes have materials assigned in OpenMC. No "unassigned" warnings.
2. **Geometry self-consistency**: `openmc.Geometry.plot_geometry()` renders without artifacts at key cross-sections.
3. **Volume comparison**: DAGMC volumes ≈ CAD reference volumes (within 1-5% depending on faceting tolerance).

## INTERFACE 5: MCNP ↔ DAGMC (Geometry Transfer)

### Key Rules
- See `instructions/dagmc.instructions.md` §MCNP Integration.
- Requires DAGMC-enabled MCNP build.
- Same material group conventions as OpenMC interface.

### Validation Rules
1. **Build compatibility**: Verify MCNP was compiled with DAGMC support.
2. **Material mapping**: Same as Interface 4 checks, adapted for MCNP material card numbers.
3. **Lost particles**: Zero lost particles in geometry checkout run.

## INTERFACE 6: natf Bridge Role

natf automates the data transfer between Steps 1-2-3 of the R2S chain:

| Transfer | natf handles automatically | User must verify |
|----------|----------------------------|------------------|
| Transport flux → FISPACT-II | Reformats mesh tally → ARBI input | Group structure consistency, normalization |
| FISPACT-II output → phtn_src | Generates phtn_src file | Bounding box flag, cooling time selection |
| phtn_src → MCNP | File is placed for MCNP to read | MCNP input references correct phtn_src path |

### natf-Specific Validation
1. **End-to-end group consistency**: Same group structure throughout Steps 1→2 (neutron) and Step 2→3 (photon).
2. **Source strength propagation**: Verify natf correctly applies source strength in the flux normalization step.
3. **Mesh identity**: natf uses the same mesh definition for flux extraction and phtn_src generation. Any mesh mismatch corrupts spatial mapping.

## INTERFACE 7: Neutronics → tricys (TBR Transfer)

`[待验证]` — 此接口的具体格式取决于 tricys 的输入方式。

### Expected Data Flow
- OpenMC/MCNP TBR calculation result → tricys input for tritium breeding rate.
- May be manual input (user copies TBR value) or file-based transfer.

### Validation Rules (generic)
1. **TBR value range**: 1.0 < TBR < 2.0 for typical fusion blankets. Values outside → suspect input error.
2. **TBR uncertainty**: If TBR uncertainty from transport is >5%, tricys results for tritium self-sufficiency are unreliable. Report the propagated uncertainty.
3. **Consistency**: TBR used in tricys must match the neutronics calculation (same blanket configuration, same enrichment, same geometry).

## UNIT CHAIN REFERENCE TABLE

| Quantity | OpenMC | MCNP | FISPACT-II | natf |
|----------|--------|------|------------|------|
| Energy | eV | MeV | eV | follows upstream |
| Flux | n/cm²-source | n/cm²-source | n/cm²/s (absolute) | converts upstream → absolute |
| Distance | cm | cm | cm | cm |
| Time | s | shakes (1e-8 s) | s/min/h/d/y (keyword) | follows FISPACT-II |
| Activity | — | — | Bq | — |
| Dose rate | — | — | — | μSv/h (MCNP output × conversion) |

## INTERFACE RED FLAGS (supplements pre-delivery-audit Non-Physical Red Flags)

The following conditions at any code interface **immediately trigger investigation**:

- Energy group count mismatch between connected codes
- Flux values negative or NaN at any interface
- Spectrum entirely zero above 1 MeV in a fast-neutron scenario (D-T, fission)
- phtn_src bounding box flag = 0
- Total photon source intensity = 0 for any activated cell
- TBR = 0 or TBR > 3.0
- SDR results uniform across a non-uniform geometry
- Factor-of-1e6 discrepancy in any quantity → likely unit conversion error (MeV↔eV or shake↔second)
