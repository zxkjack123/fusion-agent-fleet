---
description: "FISPACT-II activation/transmutation code: input format rules, spectrum handling, common pitfalls, validation checklist, and fispact-lint MCP tool integration for deterministic input validation"
applyTo: ""
revision: 2
---

# FISPACT-II — Input Format & Validation Reference

Applicable versions: FISPACT-II v4.x / v5.x (note version-specific differences where marked).

## INPUT FORMAT

### Files Block

FISPACT-II uses a keyword-driven input format. The primary input file (`input.i` or similar) contains sequential keyword blocks:

```
<keyword>
<data lines>
```

Key blocks: `FILES`, `ARBI` / `ARBF`, `FLUX`, `ZERO`, `ATOMS`, `IRRADIATE`, `COOLING`, `INVENTORY`, `PRINTALL`.

### Spectrum Input (ARBI / ARBF) — CRITICAL

The `ARBI` (arbitrary bins) keyword defines the neutron energy group structure and flux values:

1. **Group ordering**: Energy bins listed from **highest energy to lowest** (descending order). This is opposite to OpenMC's ascending `EnergyFilter` convention — conversion between codes must reverse the array.
2. **Standard group structures**: 709-group (CCFE-709), 175-group (VITAMIN-J), 69-group (GAM-II), 24-group (ABBN). The group structure **must** match the selected nuclear data library (EAF/TENDL).
3. **Flux values**: Each value is the **per-group integral flux** [n/cm²/s] for that energy bin, not a spectral density. When converting from a continuous spectrum or fine-group source, integrate over each FISPACT-II group bin.
4. **Normalization**: The sum of per-group flux values should equal the **total scalar flux** at the irradiation point. If the upstream transport code reports flux per source particle, multiply by the absolute source strength [n/s] before writing the ARBI block.
5. **Number of groups**: The first line after `ARBI` states the number of groups. This count must exactly match the number of flux values provided AND the selected library group structure.

`ARBF` is similar but defines the fission spectrum shape. Use `ARBI` for externally-provided flux spectra.

### Irradiation Sequence

- `FLUX <value>` — sets the total flux magnitude [n/cm²/s] for subsequent irradiation steps.
- `ZERO` — resets the inventory counters (use at start or between independent scenarios).
- `ATOMS <element> <amount>` — defines initial composition (atoms or grams, depending on `MASS`/`ATOMS` keyword context).
- `IRRADIATE <time> <unit>` — irradiate for the given duration. Units: `SECS`, `MINS`, `HOURS`, `DAYS`, `YEARS`.
- `COOLING <time> <unit>` — cooldown period (no flux).

### Time Step Guidance

- Irradiation steps: use sub-steps if the irradiation spans >1 order of magnitude in time relative to short-lived activation products of interest.
- Cooling steps: logarithmic spacing is typical (e.g., 1s, 10s, 1min, 1h, 1d, 1w, 1mo, 1y, ...).
- Too few steps → miss short-lived nuclide peaks. Too many steps → computational cost explosion with negligible accuracy gain.

## COMMON PITFALLS

### P1: Spectrum Group Mismatch (ROOT CAUSE OF KNOWN INCIDENT)
**Symptom**: Activation results orders of magnitude too high or too low.
**Cause**: Number of energy groups in ARBI block does not match the nuclear data library group structure. FISPACT-II may silently assign flux to wrong energy bins.
**Prevention**: Always verify `ARBI` group count matches the library (e.g., 709 for CCFE-709, 175 for VITAMIN-J).

### P2: Spectrum Truncation / Missing High-Energy Groups
**Symptom**: Threshold reactions (e.g., (n,2n), (n,α)) show zero or near-zero reaction rates despite high-energy neutrons being present.
**Cause**: Energy spectrum truncated at too low an upper bound, losing high-energy tail. Especially dangerous when fitting/interpolating spectra from transport codes.
**Prevention**: Verify spectrum upper bound covers the full source energy range (≤20 MeV for fission, ≤14.1+ MeV for D-T fusion). Cross-check with `instructions/pre-delivery-audit.instructions.md` §2.

### P3: Flux Normalization Error
**Symptom**: Activity scales linearly wrong vs. expectations.
**Cause**: Upstream flux is per-source-particle but FISPACT-II expects absolute flux [n/cm²/s]. Missing multiplication by source strength.
**Prevention**: Always document the normalization chain: source strength [n/s] × flux-per-source-particle → absolute flux [n/cm²/s].

### P4: Irradiation Time Steps Too Coarse
**Symptom**: Inventory misses short-lived intermediates; pathway analysis incomplete.
**Cause**: Single long irradiation step where sub-stepping is needed.
**Prevention**: For irradiation >1 day, split into at least 3-5 sub-steps. Check sensitivity by comparing 2-step vs. 5-step runs on a representative material.

### P5: Cooling Sequence Not Logarithmic
**Symptom**: Missing the peak activity window during early cooling.
**Prevention**: Start cooling output at ≤1 second after shutdown for short-lived isotope assessments.

## VALIDATION CHECKLIST

After running FISPACT-II, verify:

- [ ] **Total activity magnitude**: Compare total activity [Bq/kg or Bq/cm³] against order-of-magnitude expectations for the material and flux level. Structural steels under fusion-relevant flux (~1e14 n/cm²/s, 1 year): expect ~1e10–1e12 Bq/kg at shutdown.
- [ ] **Dominant nuclides**: Check top-5 activity contributors are physically reasonable (e.g., for EUROFER: ⁵⁵Fe, ⁵⁴Mn, ⁵¹Cr, ⁵⁶Mn, ⁵⁷Co are typical).
- [ ] **Cooling curve monotonicity**: Total activity should generally decrease monotonically during cooling. Non-monotonic behavior is valid only when daughter ingrowth dominates (e.g., ²¹⁰Po from ²¹⁰Bi decay) — flag and explain any increase.
- [ ] **Spectrum consistency**: Recheck that the ARBI input spectrum group count, energy range, and total flux match the upstream transport calculation.
- [ ] **Mass conservation**: Initial mass ≈ final mass (within transmutation products). Large discrepancies indicate input error.
- [ ] **Pathway reasonableness**: If pathway analysis is enabled, verify that dominant reaction channels match expected nuclear physics (e.g., (n,γ) dominant for thermal, (n,p)/(n,α) for fast spectrum).

## AUTOMATED LINT — fispact-lint MCP Server

Before submitting any FISPACT-II input for execution, call the `fispact-lint` MCP server to catch common input errors deterministically:

| Tool | Rules | Purpose |
|------|-------|---------|
| `full_scan(path)` | All 23 rules | Complete input validation |
| `check_keywords(path)` | KW-001..005 | Unknown/deprecated keywords, typos |
| `check_spectrum(path)` | SP-001..005 | ARBI/ARBF group count, ordering, normalization |
| `check_flux(path)` | FL-001..005 | FLUX value presence, spectrum consistency |
| `check_irradiation(path)` | IR-001..005 | IRRADIATE/COOLING sequence, time format |
| `check_material(path)` | MA-001..004 | MASS/DENSITY/ATOMS definitions |

**Usage protocol**:
1. After constructing or modifying a FISPACT-II input file, call `full_scan(path)` with `min_level="warning"`.
2. Fix all `error`-level findings before execution. `warning`-level findings should be reviewed.
3. `info`-level findings are advisory (non-numeric values, missing optional data).
