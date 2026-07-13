---
description: "Numerical intuition pitfalls for nuclear engineering simulation agents. Encodes the smell-detection heuristics experienced nuclear engineers apply unconsciously: physically impossible quantities, suspicious patterns, and common normalization/debugging mistakes. 核工程数值直觉陷阱：编码资深核工程师的经验判断——物理不可能值、可疑模式、常见归一化/调试错误。"
applyTo: simulation-builder,simulation-analyst,fusion-chain-runner,data-analyst,doublecheck,fusion-deep-research
target_agents:
  - simulation-builder
  - simulation-analyst
  - fusion-chain-runner
  - data-analyst
  - doublecheck
  - fusion-deep-research
version: 1
revision: 1
---

# Nuclear Engineering Numerical Intuition — 核工程数值直觉陷阱

Experienced nuclear engineers develop subconscious pattern-matching heuristics that flag "this doesn't look right" long before formal validation catches it. This document encodes those heuristics for AI agents that lack the years of hands-on experience that build this intuition.

**Use this catalog**: After extracting or computing any numerical result, scan this list before reporting. If any pattern matches, investigate before delivering.

## §1: Physically Impossible Values (hard stop)

| Pattern | Signal | Root Cause | What to Do |
|---------|--------|-----------|------------|
| `peak < average` for any distributed quantity | Peak flux/heating/dose lower than spatial average | Normalization error, mesh resolution failure, tally filter misconfiguration | **HARD STOP** — physically impossible. Check normalization first. |
| Negative flux, cross-section, concentration, or density | Any physics quantity < 0 | Statistical noise overwhelming signal, incorrect tally weight, MCNP lost-particle artifacts | Increase particle count; check tally volume normalization; verify no void regions in tally mesh |
| TBR < 0 or > 3.0 | Tritium breeding ratio outside all known physical regimes | Neutron source normalization error, missing material, geometry void | Check source strength; verify all blanket regions included in tally |
| keff < 0.5 or > 1.5 for typical reactor systems | Extreme eigenvalue | Missing fissionable material, missing absorber, incorrect cross-section library | Verify material definitions; check for void regions where fuel should be |
| Zero flux in expected non-void region | All-group flux = 0 where material exists | Material assigned as void, tally filter excludes region, importance = 0 incorrectly set | Check material assignments; verify tally filter coverage; check importance cards |
| Energy-integrated flux > source strength | Total flux exceeds total source | Double-counting in tally, incorrect normalization, source normalization applied twice | Audit normalization chain: per-source-particle → absolute → energy-integrated |

## §2: Suspicious Patterns (requires explanation)

| Pattern | Signal | Possible Explanation | Diagnostic |
|---------|--------|---------------------|------------|
| **Flat-profile anomaly** | Flux or heating is nearly constant across a region with strong material gradients | Tally resolution too coarse, importance biasing over-smoothing, energy group collapse | Refine mesh; check for uniform importance; increase energy groups |
| **Sharp spatial transition without material boundary** | 10× jump in flux at a location with no geometry change | Mesh boundary artifact, tally filter discontinuity, volume normalization error at cell boundary | Overlay tally mesh on geometry; check volume fractions at boundaries |
| **Symmetric pattern in asymmetric geometry** | Flux pattern shows mirror symmetry where geometry is asymmetric | Incorrect boundary condition (reflective where vacuum expected), source symmetry not broken | Check boundary conditions; verify source position/orientation |
| **Energy spectrum with unphysical peaks** | Peak in energy bin where no source particles exist (e.g., 100 MeV peak in fission spectrum) | Statistical noise, energy bin mislabeling, incorrect group structure assignment | Check energy bin assignments; verify source spectrum boundaries |
| **All tallies have identical relative error** | Every tally shows exactly the same statistical uncertainty | Copy-paste error in post-processing, script applying same uncertainty to all outputs | Audit post-processing script for hardcoded uncertainty value |

## §3: Unit Confusion Patterns (the 1e6 killer)

| Pattern | Signal | Root Cause |
|---------|--------|-----------|
| **Result off by exactly 1e6 (or 1e3, 1e-6, etc.)** | Any quantity is 10^±3 or 10^±6 times expected | eV ↔ MeV confusion, cm ↔ m confusion, barn ↔ cm² confusion |
| **Source energy in eV, tally flux in MeV (or vice versa)** | Energy-dependent results don't align with known cross-section features | OpenMC uses eV; MCNP6 SDEF uses MeV. Mixed-code workflows are the highest risk. |
| **Density 1e3× or 1e-3× expected** | Material density is suspiciously close to 1.0 or 1000 | g/cm³ vs kg/m³ confusion |
| **Flux normalization off by factor of source_particles** | TBR or reaction rate off by exactly the number of source particles | Forgot to divide by source particles (per-source-particle vs absolute normalization) |

## §4: Code-Specific Intuition

### OpenMC
| Pattern | Expectation |
|---------|------------|
| `openmc.config['cross_sections']` not set → all tallies = 0 | OpenMC silently runs without cross-sections |
| `EnergyFilter` bins not ascending → NaN in tally | Energy bins must be monotonically increasing in eV |
| CellFilter missing a cell → that cell is not tallied | No warning — partial tally coverage is a silent error |
| `Material.macroscopic_data()` returns None → no xs in library | Check nuclide availability; may need different temperature |

### MCNP6
| Pattern | Expectation |
|---------|------------|
| SDEF energy units = MeV (not eV) | MCNP convention is MeV for source; OpenMC is eV |
| `imp:n=0` on cell containing material → zero tallies there | Importance-based particle killing — intentional or bug? |
| Tally fluctuation chart (TFC) test 10 fails → biased result | Statistical test failure means result may be unreliable even with small relative error |
| `lost` particles >1% → geometry or importance error | Check for particles trapped in low-importance or complex geometry regions |

### FISPACT-II
| Pattern | Expectation |
|---------|------------|
| ARBI spectrum descending (high→low) vs OpenMC ascending (low→high) | Energy group ordering is opposite between codes |
| Group count mismatch → total activity off by factor | FISPACT requires exact group count match to library definition |
| Per-group flux in per-source-particle → activity 1/nps× too low | Must multiply by source strength before FISPACT flux input |
| Cooling time in seconds, not years → vastly overestimated decay | FISPACT time units depend on input format (ATOMS vs SECONDS) |

## §5: Verification Heuristics (the "does this look right" checklist)

Before reporting any result, apply these five checks. Each takes <10 seconds for an experienced engineer but catches 80% of mistakes:

1. **Unit sanity**: Is the number in the right ballpark with these units? Would changing eV→MeV make it reasonable?
2. **Continuity**: Are spatially adjacent values physically continuous? Sharp jumps without material boundaries are bugs.
3. **Monotonicity**: Should this quantity increase or decrease with this parameter? If the trend is physically impossible (e.g., TBR decreasing with Li-6 enrichment in a well-moderated system), investigate.
4. **Conservation**: Do input and output quantities balance? Source neutrons = absorbed + leaked + (1/keff-1)×fission? Total heating = sum of per-region heating?
5. **Literature band**: Is this result consistent with published values for similar configurations? Within 2× is acceptable; >5× requires explanation; >10× is almost certainly an error.

## §6: Common Debugging Sequence

When a result looks wrong, apply this diagnostic flow in order. Do NOT jump to step 5 before checking steps 1-4 (this is the #1 debugging mistake).

1. **Normalization check**: Is the flux normalized correctly? Per-source-particle → absolute → tally-specific?
2. **Geometry check**: Are all regions in the tally? Any voids where material should be or vice versa?
3. **Energy check**: Do energy bins cover the source spectrum? Is the bin ordering correct for this code?
4. **Material check**: Are all nuclides available in the cross-section library at the correct temperature?
5. **Cross-code validation**: Run a minimal version of the same problem in a different code if possible.
6. **Literature benchmark**: Compare with published results for the same/similar configuration.

## Integration

This catalog should be referenced:
- In Simulation Builder Stage E (Validation & Pre-flight) — scan for §1 and §3 patterns
- In Simulation Analyst Stage B.5 (CT physical-quantity challenge) — use §5 heuristics
- In Data Analyst post-extraction — scan for §2 patterns
- In Doublecheck Layer 3 adversarial review — use §1 as non-negotiable detection rules
