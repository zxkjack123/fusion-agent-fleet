---
name: "literature-band-validation-suite"
description: "Build a multi-benchmark validation suite that compares a numerical/surrogate model against literature reference bands. Each benchmark = (literature CSV with `# source:` + `# units:` headers) + (parametric `test_in_band` + monotonicity tests + sanity tests) + (xfail-with-KNOWN_ISSUES.md for documented surrogate deviations). Closes the loop with a one-shot pytest runner that emits a markdown summary table. 文献对标验证套件, 量级带验证, 单位声明断言, xfail 已知偏差跟踪, pytest 参数化, 仿真模型对标文献, validation benchmark suite, reference band check."
revision: 1
---

# Literature-Band Validation Suite

> Crystallized from: phase1-validation-benchmarks (10 tasks: 9 benchmarks A1/A2/B1/B2/B3/C1/C2/D1/D2 + E1 runner; 70 tests, 1 documented xfail)
> Date: 2026-04-27
> Trigger: T1 (≥5 distinct tool-call steps per task × 10 tasks) + T3 (user explicit "固化")

## When to Use

- A numerical model (Monte Carlo, ODE, surrogate, fitted formula) needs to be **validated against published literature** rather than only against API self-consistency.
- The model has multiple physical sub-modules, each with at least one literature reference (textbook, journal table, established benchmark code) that defines a value or band.
- Acceptance is naturally expressed as "result lies in band [x_min, x_max]" with order-of-magnitude or factor-of-N tolerance — exact reproduction of one published number is NOT required.
- Source modules must remain **frozen** during validation (only test files and reference data may be added). Any deviation is recorded, not fixed.
- A pytest-based test infrastructure already exists or is acceptable to introduce.

## When NOT to Use

- Validation requires **bit-exact** reproduction of a benchmark code's output → use a regression-test pattern with golden files instead.
- The "literature reference" is the user's own prior simulation result (no external corroboration) → this is regression testing, not literature validation.
- Single-formula sanity check with no reference data needed → write a single pytest, no need for the full suite scaffolding.
- The model is still being designed/iterated; expected bands are unknown → defer until at least one reference can be cited.
- Reference data is proprietary and cannot be committed to the repo → adapt to load from external paths, but the pattern still applies.

## Workflow

### Phase A: Plan & Scaffold

1. Identify the validation scope: enumerate sub-modules to be benchmarked. Each becomes one task `T-X<n>` (e.g., A1 atomic rates, B1 model analytic limit, C1 transport benchmark, D1 system-level scaling).
2. For each benchmark, write a plan task with: **目标** / **依赖** / **修改内容** (CSV path + test file path) / **修改边界** (no source modification) / **验收标准** (named criteria) / **潜在风险**.
3. Add a final infrastructure task `T-E1`: shared `conftest.py`, `run_all.py` summary generator, `KNOWN_ISSUES.md` for documented xfails.
4. Create `phase1_3d/validation/` (or equivalent) with `__init__.py` and `reference_data/` subdirectory.

### Phase B: Execute Per Benchmark

For each `T-X<n>`:

1. **Sanity-probe the model** with a quick `python -c "..."` to discover actual output magnitudes. This determines realistic band boundaries and reveals surrogate-model deviations early.
2. **Write the reference CSV** at `validation/reference_data/<source>_<topic>.csv`. Mandatory header lines:
   ```
   # source: <Author Year, Journal Vol Page, table/figure ref + cross-checks>
   # units: <T_eV in eV; sigmav in m^3/s; ...>
   # columns: <col1,col2,...>
   ```
   Each test MUST `assert "# units:" in raw` after reading the CSV — this is the unit-confusion trap (m³/s vs cm³/s, eV vs keV).
3. **Write `test_bm_<x>_<topic>.py`** with these test types in order:
   - **Pointwise / band-membership**: parametric `test_in_band(case)` reading the CSV, asserting `pytest.approx(ref, rel=...)` or `min ≤ result ≤ max`.
   - **Magnitude/unit-guard**: an explicit hard bound (e.g., `1e-15 < sv < 1e-13`) that catches a unit-system swap.
   - **Boundary**: zero/negative input, edge of definition domain.
   - **Monotonicity**: directional consistency (higher density → shorter MFP, larger grain → longer ablation).
   - **Limit case**: model degenerates to known analytical formula (e.g., G→1 no-shielding, n_e=0 vacuum ballistic).
4. **Run** `python -m pytest validation/test_bm_<x>_*.py -v`. Iterate until all tests pass OR the deviation is genuine.
5. **If a deviation is genuine** (model output outside literature band, but root cause is a documented surrogate limitation):
   - Append a section to `validation/KNOWN_ISSUES.md` with: expected band, observed value, root cause analysis, resolution path.
   - Mark the failing test with `@pytest.mark.xfail(reason="...", strict=True)`.
   - Do NOT modify the source module to make the test pass.
6. **Mark** `#### Task X<n>: ...` → `#### ✅ Task X<n>: ...` in plan.
7. **Commit** all benchmark files (CSV + test + KNOWN_ISSUES.md if updated) + plan in one commit: `[Plan: <plan-name>] Task X<n>: <topic>`.

### Phase C: Infrastructure Task (T-E1)

1. `conftest.py`: shared fixtures (e.g., `wall`, default profile, `flat_sol_factory` for uniform-plasma limits).
2. `run_all.py`: subprocess-pytest + parse `PASSED`/`FAILED`/`XFAIL` per file → emit `VALIDATION_SUMMARY.md` with per-benchmark pass/fail/xfail counts.
3. Run `python -m phase1_3d.validation.run_all`, verify summary table renders correctly, commit.

## Inputs & Outputs

| Input | Source |
|-------|--------|
| Frozen source modules | `<package>/<sub-module>/*.py` (read-only during validation) |
| Literature references | Published papers, textbooks, established benchmark tables (cited in CSV `# source:` header) |
| Plan file | `.github/plans/<phase>-validation-benchmarks.md` |

| Output | Format |
|--------|--------|
| Reference data | `<package>/validation/reference_data/<source>_<topic>.csv` with `# source:` + `# units:` headers |
| Per-benchmark test | `<package>/validation/test_bm_<id>_<topic>.py` |
| Known issues registry | `<package>/validation/KNOWN_ISSUES.md` |
| Shared fixtures | `<package>/validation/conftest.py` |
| One-shot runner | `<package>/validation/run_all.py` |
| Summary report | `<package>/validation/VALIDATION_SUMMARY.md` (auto-generated) |
| Per-task git commits | `[Plan: <plan-name>] Task X<n>: <topic>` |

## Common Pitfalls

- **Self-referential reference data**. If the CSV is computed from the same coefficients the model uses, the test only catches transcription errors, not physics errors. Mitigation: cross-check at least one CSV value against an independent secondary source (different paper, ADAS table, benchmark code), and document the cross-check in the `# source:` header.
- **Missing unit declaration assertion**. Reading the CSV with `numpy.loadtxt(skip_header=...)` silently strips comments. Always read raw text first, assert `"# units:"` in it, then parse — this catches CSVs whose units were silently changed.
- **Tolerance set after seeing the result**. Set `rel=` based on literature inter-source spread or stated experimental uncertainty BEFORE running the test, not after. If you have to relax tolerance to make a test pass, that's a finding, not a fix — record it.
- **Sanity-probe too late**. Always sanity-probe the model output (`python -c "..."`) BEFORE writing the test. Discovering a 100× deviation after writing 5 carefully-tuned tests wastes effort and biases tolerance choices.
- **xfail without KNOWN_ISSUES.md entry**. Every `@pytest.mark.xfail` MUST link to a documented root-cause analysis. Use `strict=True` so an unexpected pass becomes a failure (signals the underlying issue was silently fixed and the xfail should be removed).
- **Iteration loop accumulating dt drift**. For time-integrated tests (full ablation, full trajectory), use adaptive step `dt = min(dt_max, frac * |state| / |rate|)` rather than fixed dt — prevents missing termination conditions when the rate is small near the end.
- **Flat-plasma fixture trap**. To create a "uniform plasma" limit for analytical comparisons, set `lambda_n = lambda_T = 1e10` AND set `n_e_floor = 0.99 * n_e_sep` (otherwise the floor clamps to a default 1e16 and creates a discontinuity). Same applies to any exponential-decay-with-floor profile.
- **MC particle conservation false-positive**. The conservation invariant `emitted = ionized + absorbed` may hold for default parameters but fail when particles run out of `max_steps` (silent escape). Always print `emitted - ionized - absorbed` in the sanity probe; if non-zero, document the escape branch as a separate test, not as a conservation check.
- **Metadata-vs-physics parameter decoupling**. A parameter named `pump_port_area` may be a metadata/validation field with no effect on the simulation kernel, while the actual aperture is set by `pump_port_half_width`. Confirm by reading the source — never assume parameter names match physics. This is a frequent xfail source.
- **Plan and acceptance criteria drift**. The plan-stated acceptance band ([0.1, 10] m³/s) may not be achievable by the surrogate (gives 0.02 m³/s). Resolve by xfail+KNOWN_ISSUES, NOT by relaxing the band — relaxing the band hides the deviation from future readers.

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-04-27 | Initial crystallization | phase1-validation-benchmarks (10 tasks; 70 tests, 1 xfail; commits 88b8564..HEAD on pB-Fuel-Cycle/master) |
