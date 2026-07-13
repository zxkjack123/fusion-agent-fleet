---
name: scientific-troubleshooting
description: "Scientific result troubleshooting diagnostic workflow for nuclear engineering simulation and data analysis: 5-stage structured debugging protocol to identify root causes when simulation outputs, experimental data, or analysis results do not make physical sense. 科研排障：仿真结果异常、实验数据矛盾、分析数据不合理时的五阶段诊断方法，用于定位根因而非盲目试错。"
revision: 1
---

# Scientific Troubleshooting — 科研排障诊断方法

## When to Use

- Simulation output (TBR, keff, SDR, DPA, activity, dose rate, etc.) is outside expected physical range
- Extracted data contradicts prior expectations or literature values
- Analysis result violates a known physical constraint (conservation, monotonicity, positivity)
- Experimental data and simulation results disagree beyond expected uncertainty
- Any "this doesn't make sense" moment in scientific computing

## When NOT to Use

- Pure code bugs (syntax errors, import failures, type mismatches) — use standard debugging
- Environment/configuration issues (missing packages, wrong paths, MCP unavailability)
- Known code-specific errors with documented fixes (e.g., MCNP lost-particle artifacts)
- Simple unit conversion mistakes that are immediately obvious from inspection

## Workflow (5-Stage Diagnostic Protocol)

Execute stages in order. Do NOT skip to Stage 5 before completing Stages 1-4. This is the single most common troubleshooting mistake — jumping to "let me change the input parameters" before checking basic normalization.

---

### Stage 1: Stop & Observe — 停止并观察

Before acting, characterize the anomaly precisely:

1. **What exactly is wrong?** State the anomalous result in quantitative terms with units.
2. **How far is it from expected?** Compute the ratio: `observed / expected`. Is it within 2×? 10×? 100×?
3. **Is the direction physically possible?** A TBR < 0 is impossible. A peak < average is impossible. A negative flux is impossible. If the result is physically impossible → go directly to Stage 2 (Normalization Audit). If merely surprising → go to Stage 3 (Cross-Check).
4. **What changed since the last "known good" result?** List all input/code/environment changes.

**Decision tree**:
- Physically impossible → Stage 2 (normalization or geometry error most likely)
- Possible but surprising → Stage 3 (could be real physics or measurement artifact)
- Fluctuating / non-reproducible → Stage 2 (statistical or convergence issue)

---

### Stage 2: Normalization Audit — 归一化审计

The #1 cause of "impossible results" is normalization error. Check in order:

1. **Per-source-particle → absolute normalization**: Is the flux normalized to per-source-particle or absolute? Did you multiply by source strength?
2. **Volume normalization**: For mesh tallies, are volume fractions correctly computed? In CAD-based geometry, are cell volumes from the mesh overlaid correctly?
3. **Energy group normalization**: For spectrum tallies, did each group's flux get divided by the bin width (if needed)?
4. **Cross-code normalization**: In multi-code chains (OpenMC→FISPACT), did the flux get converted from per-source-particle to absolute before use as FISPACT input?
5. **Statistical convergence**: Check relative errors. Are all tallies with relative error >10% flagged? Any tallies with zero values where non-zero expected?

**Anti-pattern**: "I multiplied by source strength but these numbers still look wrong" → check if source strength was applied **twice** (once in the script, once in post-processing).

---

### Stage 3: Cross-Check — 交叉验证

If normalization passes audit, verify the result against independent sources:

1. **Analytic solution**: Does a simplified version of the problem have an analytic solution? (e.g., infinite-medium spectrum, point-source attenuation)
2. **Literature benchmark**: Query `dify-knowledge/global_search` for published results of the same/similar configuration. Within 2× is reassuring; >5× needs explanation; >10× is almost certainly an error.
3. **Conservation law**: Does the result respect known conservation laws? Neutron balance, energy conservation, mass balance?
4. **Cross-code**: Can a similar calculation be done quickly in a different code to compare?
5. **Order-of-magnitude**: Use back-of-envelope estimation. Given source strength S and material attenuation μ, what order of magnitude should the result be?

**Decision tree**:
- Cross-check agrees within 2× → maybe the original expectation was wrong; continue to Stage 4
- Cross-check disagrees by >5× → one of the two setups has an error; isolate which one by simplifying both

---

### Stage 4: Root Cause Hypothesis — 根因假说

Formulate specific, testable hypotheses about what causes the anomaly:

1. **List all plausible causes** (3-5 minimum). Do NOT anchor on the first idea.
2. **Rank by likelihood**: For each cause, estimate P(cause) × P(observing-this-symptom | cause).
3. **Design a minimal test** for the top-ranked cause:
   - Test should change exactly one thing
   - Test should have a clear PASS/FAIL criterion
   - Test should take as little compute as possible
4. **Test the top 2 hypotheses**. If neither explains the anomaly, test the 3rd and 4th.
5. **If all plausible causes tested and refuted**: Escalate. "The anomaly has no explanation within known failure modes." Do NOT invent a cause.

**Common root causes by symptom**:

| Symptom | Top 3 Causes (in order) |
|---------|-------------------------|
| Result off by 1e6 | eV↔MeV, cm↔m, barn↔cm² unit confusion |
| Result off by 1e3 | g/cm³↔kg/m³ density confusion |
| Result off by nps | Forgot to divide by source particles |
| Zero result where non-zero expected | Material assigned as void, tally filter misconfiguration, cross-section not in library |
| Non-zero result where zero expected | Leakage into void region, importance/cutoff contamination |
| All tallies have identical uncertainty | Post-processing script applying same value to all; never a real convergence artifact |
| keff shift >500 pcm without geometry change | Wrong cross-section library, missing material, eigenvalue not converged |

---

### Stage 5: Fix & Verify — 修正并验证

1. **Apply the fix** from Stage 4's top-ranked hypothesis.
2. **Re-run** the minimal test.
3. **Verify** the result is now physically reasonable.
4. **Check for unintended consequences**: Did fixing the normalization break downstream calculations?
5. **Document** what was changed and why, in the CT Red Flag Issue Ledger format:
   ```
   🔧 FIXED: peak_factor was 0.86 because tally normalization applied source strength twice.
   After correction: peak_factor = 2.3, consistent with expectation.
   ```
6. **Full re-run**: If the fix changes input parameters, re-run the full workflow, not just the failing step.

---

## Common Pitfalls

1. **Skipping to Stage 5**: The "let me just change the mesh and re-run" instinct. Normalization errors (Stage 2) cause >50% of anomalous results; changing mesh won't fix a missing source-normalization step.
2. **Anchoring on one hypothesis**: Formulating H1 ("must be the Li-6 enrichment") and only testing H1. Always generate 3-5 hypotheses and test the top 2.
3. **Changing multiple things at once**: "I'll re-run with better mesh, updated cross-sections, and source normalized — one of those should fix it." No. If you fix it, you don't know which fix worked, and you may have introduced a compensating error that hides the real bug.
4. **Trusting the first "now it looks right" result**: After a fix, the new result may look physically reasonable by coincidence (two errors canceling). Verify against an independent check (Stage 3).
5. **Not checking cross-code interface units**: OpenMC uses eV; MCNP SDEF uses MeV. FISPACT ARBI is descending; OpenMC EnergyFilter is ascending. These interface conventions are the single highest-risk failure point in multi-code workflows.
6. **Treating statistical noise as physical signal**: A tally with relative error 0.30 may show a "feature" that is purely statistical. Check relative error before interpreting spatial structure.
7. **Ignoring warnings from input validators**: openmc-validator and fispact-lint warnings are often treated as informational but frequently flag the root cause. If a validator issues a WARNING about something you later observe as anomalous, trust the warning.
8. **Not recording the fix**: "I fixed it, now it works" without documentation means the same error will recur in the next project. Always record the fix in a format that survives session boundaries.

## References

- `instructions/numerical-intuition-pitfalls.instructions.md` — Physical value sanity checks
- `instructions/pre-delivery-audit.instructions.md` — Pre-delivery quality gate
- `instructions/post-tool-reconciliation.instructions.md` — Post-tool reconciliation protocol
- `instructions/multi-code-interface.instructions.md` — Cross-code normalization rules
- `docs/failure-modes.md` — Cataloged failure patterns (FM-001 to FM-013)

## Revision Log

- **rev 1 (2026-07-02)**: Initial version. Encoded from numerical-intuition-pitfalls catalog, FM catalog, and user-reported peak-factor-below-one incident.
