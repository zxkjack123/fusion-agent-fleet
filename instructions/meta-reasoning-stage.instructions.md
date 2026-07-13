---
description: "Pre-execution meta-reasoning protocol for scientific agents: problem classification, domain prior loading, uncertainty quantification, benchmark declaration. Applies to Simulation Builder, Simulation Analyst, and Fusion Deep Research prior to any compute-intensive work. 元推理协议：问题分类、领域先验加载、不确定性量化、基准声明。在投入计算资源前完成，避免方向性错误。"
applyTo: simulation-builder,simulation-analyst,fusion-deep-research
target_agents:
  - simulation-builder
  - simulation-analyst
  - fusion-deep-research
version: 1
revision: 1
---

# Meta-Reasoning Stage — 元推理协议

Inspired by Google Co-Scientist (Nature, 2026) and the scientific method itself. This protocol executes **before any compute-intensive work** (simulation build, data analysis, deep research) to ensure the agent is solving the right problem with the right expectations, rather than discovering mid-way that the direction was wrong.

**Core principle**: Spending 5% of total budget on meta-reasoning prevents 50% of wasted effort from wrong turns.

## Four-Step Protocol

Execute all four steps in sequence. At low depth/quick scans, steps 3 and 4 may be abbreviated but must not be skipped entirely.

---

### Step 1: Problem Classification — 问题分类

Classify the user's request into one of the following categories. If ambiguous, ask the user before proceeding.

| Category | Typical Signal | Risk Profile | Budget Strategy |
|----------|---------------|-------------|-----------------|
| **Parameter Exploration** | "Sweep X from A to B", "What happens if...", "How does Y change with Z?" | Missing boundary conditions, parameter range physically invalid | Uniform grid over range; verify min/max are physical |
| **Hypothesis Testing** | "Is X caused by Y?", "Does A explain B?", "My theory predicts..." | Confirmation bias, failing to test null hypothesis | Explicit H0 statement; design test that could refute |
| **Anomaly Investigation** | "Why is X different from expected?", "This result doesn't make sense", debugging | Chasing wrong root cause, anchoring on first explanation | List all plausible causes; rank by likelihood; test top-2 |
| **Optimization** | "Find the best X to maximize Y", "Optimize for Z subject to constraints" | Local optimum, overfitting, constraint violation | Sample broadly first; verify optimum with perturbation |
| **Benchmarking / Validation** | "Compare with experiment", "Validate against literature", "Cross-check" | Apples-to-oranges comparison, cherry-picking benchmarks | Pre-commit comparison criteria; declare expected agreement range |

**Output**: A one-line classification + justification:
```
## Problem Classification
**Type**: Hypothesis Testing
**Justification**: User claims "Li-6 enrichment is the dominant uncertainty for TBR at high temperatures" — this is a falsifiable hypothesis about mechanism, not just parameter exploration.
**Risk**: Confirmation bias — user may have already collected supporting evidence and seeks validation. Must explicitly test H0: "Li-6 enrichment is NOT the dominant uncertainty above 900 K."
```

---

### Step 2: Domain Prior Loading — 领域先验加载

Before doing ANY work, load the domain priors that constrain the problem:

1. **Expected value ranges**: Query `dify-knowledge/global_search` for published value ranges of key quantities. Use `fusion-params/query_*` if quantitative data is needed. Note the typical range, not a single value. Also scan **READ `instructions/numerical-intuition-pitfalls.instructions.md` before starting** — contains critical rules §1 (physically impossible values) and §4 (code-specific traps) relevant to this code/physics.
2. **Common failure modes**: Query `dify-knowledge/global_search` for known pitfalls specific to this code/material/physics scenario. Also read `docs/failure-modes.md` for cataloged failure patterns relevant to this task.
3. **Physical constraints**: Identify what conservation laws, symmetry constraints, or known bounds apply (e.g., TBR must be >0, flux must be non-negative, energy must be conserved).
4. **Available benchmarks**: Query `dify-knowledge/global_search` for validated benchmark cases or experimental data that can serve as ground truth.

**Output**: A compact prior ledger:
```
## Domain Priors
| Quantity | Expected Range | Source | Constraint |
|----------|---------------|--------|------------|
| TBR (HCPB @ 30% Li-6) | 1.05–1.25 | KB: BEST dataset, fusion-params | Must be >0; < TBR_max for pure Li-6 |
| keff (HCPB critical) | 1.00 ± 0.02 | KB: fusion-params | Must be >0 |
| Peak nuclear heating (FW) | 5–30 W/cm³ | ITER TBM literature | Must not exceed material limits |
| n-flux (first wall) | 1e14–5e14 n/cm²/s | D-T source at 1 MW/m² wall loading | Linear with source strength |

## Known Failure Modes (from docs/failure-modes.md and KB)
- MCNP6 vs OpenMC eV/MeV unit confusion → verify source energy units per code
- Mesh tally normalization error → double-check flux normalization chain
- TBR zone partitioning double-counting → verify tally filter coverage without overlap
- Peak/average ratio < 1.0 → normalization or mesh resolution error

## Benchmarks Available
- ITER TBM baseline (TBR=1.15±0.08, heating=18 W/cm³) [DOI: ...]
- HCPB mock-up experiment at FNG [KB: BEST dataset]
```

---

### Step 3: Uncertainty Quantification — 不确定性量化

Identify which input parameters dominate the output uncertainty, so budget can be concentrated on them.

1. **Sensitivity ranking**: List all variable input parameters and rank by expected impact on the key output. Use `dify-knowledge/global_search` to find prior sensitivity studies. If none are available, use physical reasoning (e.g., cross-section uncertainty in resonance region matters more than in smooth region).
2. **No-regret parameters**: Parameters where the exact value barely matters — set to a reasonable default and move on.
3. **High-impact list**: Parameters where small changes produce large output swings — these get extra verification budget.
4. **Budget allocation**: Proportion research/compute budget to sensitivity rank: top-ranked parameter gets ≥40% of total. Don't spend equal time on everything.

**Output**: A ranked sensitivity table with budget allocation:
```
## Uncertainty Quantification
| Rank | Parameter | Sensitivity | Budget | Rationale |
|------|-----------|------------|--------|-----------|
| 1 | Li-6 enrichment | HIGH (±10% → TBR shift ±0.08) | 40% | Dominates TBR; cross-check with ICP-MS measurement data |
| 2 | Breeder zone thickness | MEDIUM (±1 cm → TBR shift ±0.03) | 30% | Engineering constraint; verify CAD model |
| 3 | Nuclear data library | MEDIUM (ENDF/B-VIII vs JEFF-3.3 → TBR shift ±0.02) | 20% | Document which library; optional comparison run |
| 4 | Source spectrum shape | LOW (Gaussian vs Muir → <1% TBR shift) | 10% | No-regret: use Muir for D-T fusion |
| 5 | Mesh resolution | LOW (1cm→5mm → <0.5% TBR shift) | 0% (verify once) | No-regret: use finest affordable mesh |

**Budget strategy**: Heavy on Li-6 (the dominant uncertainty), light on mesh (convergence check only).
```

---

### Step 4: Benchmark Pre-Declaration — 对比基准声明

Before producing any results, declare the expected outcome to create an explicit reference frame that makes surprises visible.

1. **Expected value with range**: For each key output, state what you expect AND what would be surprising.
2. **Surprise definition**: Define what constitutes a "this doesn't make sense" result — a trigger to halt and re-examine assumptions.
3. **Pre-committed acceptance criteria**: What must be true for the result to be acceptable?
4. **Elo-style prior ranking** (fusion-deep-research only): Use the existing Elo Hypothesis Tournament to rank hypotheses. For simulation agents, use a simpler format.

**Output**: A pre-commitment table:
```
## Benchmark Pre-Declaration
| Output | Expected | Acceptable Range | SURPRISE Trigger | Current Hypothesis |
|--------|----------|-----------------|-------------------|---------------------|
| TBR | 1.12 | 0.95–1.30 | <0.5 or >2.0 → likely normalization error | Elo #1: "Lithium burnup is the dominant TBR loss mechanism at high temperature" |
| TBR @ 90% Li-6 | 1.25 | 1.10–1.45 | <1.0 → self-shielding too strong, check geometry | Elo #2: "Neutron spectrum hardening at high enrichment increases parasitic absorption in structure" |
| keff | 1.045 | 1.03–1.06 | <0.95 or >1.10 → missing material or geometry error | (single hypothesis) |
| Peak nuclear heating (FW) | 18 W/cm³ | 10–35 W/cm³ | <1 or >100 → units error or normalization failure | (single hypothesis) |

**Surprise Protocol**: If any output falls in the SURPRISE range:
1. HALT — do not proceed with further calculations
2. Check the most likely root cause (see Known Failure Modes from Step 2)
3. If cause is identified and corrected → re-run and compare
4. If cause remains unknown → escalate to user with full diagnostic information; do NOT invent an explanation
```

---

## Depth-Scaling Rules

| Depth | Steps Required | Budget |
|-------|---------------|--------|
| **quick** / **L1-Lite** | Steps 1 (classification) + 2 (abbreviated: 1–2 priors only) | ~3% |
| **standard** / **L2-Standard** | Steps 1 + 2 (full) + 3 (abbreviated: top-3 parameters) | ~5% |
| **deep** / **L3-Critical** | All 4 steps (full) + Elo Tournament (FDR only) | ~8% |

## Integration Points

| Agent | Insert Before | Special Notes |
|-------|--------------|---------------|
| **Simulation Builder** | Stage A (Requirements & Constraints) | Step 3 helps avoid sweeping irrelevant parameters; Step 4 declares what "reasonable results" look like before the first mesh is built |
| **Simulation Analyst** | Stage A (Data Identification) | Step 2 loads expected ranges for plausibility comparison; Step 4 prevents post-hoc criteria reframing |
| **Fusion Deep Research** | Stage 0 (Task Decomposition) | Merges with existing Hypothesis Tournament (Stage 0.5) and Elo Tournament (Stage 0.6); Steps 3-4 complement existing budget allocation |

## Fallback

If any KB query in Steps 2-3 returns empty (e.g., Dify unavailable, no prior sensitivity studies found):
- Record the gap: `[KB unavailable — using internal knowledge only]`
- Use physical reasoning and documented ranges from `corpora/plausibility-ranges.yaml`
- Annotate lower confidence on priors: `[Confidence: LOW — no KB confirmation]`
- Continue with the protocol anyway — even incomplete priors are better than no priors

## See Also

- `instructions/co-scientist-mechanisms.instructions.md` — Elo Hypothesis Tournament, Meta-Review Feedback Loop, Verify-Heavy Budget
- `instructions/pre-delivery-audit.instructions.md` — Physical plausibility gate (post-execution counterpart)
- `corpora/plausibility-ranges.yaml` — Canonical physical quantity ranges
- `docs/failure-modes.md` — Cataloged failure patterns
