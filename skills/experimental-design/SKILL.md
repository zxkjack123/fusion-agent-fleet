---
name: experimental-design
description: "Design of experiments (DOE) for nuclear engineering simulation — randomization, blocking, factorial/fractional factorial, response-surface, Latin hypercube sampling. Use when: planning parameter sweeps, blanket optimization DOE, shielding layer Latin hypercube, activation experiment randomization. 实验/仿真设计：包层参数 DOE、屏蔽层优化拉丁超立方、活化实验随机化。"
revision: 1
---

# Experimental Design (DOE) for Nuclear Engineering

## When to Use

- Planning parameter sweeps BEFORE submitting HPC jobs
- Designing blanket/shield multi-factor optimization studies
- Screening many parameters to find the few that matter (fractional factorial)
- Response-surface optimization when curvature matters (central composite, Box-Behnken)
- Space-filling exploration of continuous parameter spaces (Latin hypercube)
- Randomization and blocking to avoid confounding with batch/run-order effects
- Pre-registration of simulation studies for reproducibility

## When NOT to Use

- Single-parameter variation (just use manual runs or `parametric-sweep` skill)
- For statistical power/sample size — use `scikit-learn-ml` for power analysis
- For analyzing data after collection — use `data-analyst` agent or `scikit-learn-ml`
- For post-hoc sensitivity analysis — use sklearn permutation importance

## Design Decision Tree

```
What are you optimizing/exploring?
│
├─ Compare a few discrete conditions (A vs B vs C)?
│   └─ RANDOMIZED BLOCK design (block on HPC batch/node/day)
│
├─ Screen MANY parameters (5+) to find the few that matter?
│   └─ FRACTIONAL FACTORIAL or PLACKETT-BURMAN screening
│
├─ Quantify main effects AND interactions among ≤5 factors?
│   └─ FULL 2^k FACTORIAL design
│
├─ Find the settings that OPTIMIZE a response (curvature expected)?
│   └─ RESPONSE-SURFACE: central composite or Box-Behnken
│
└─ Explore a simulation space with continuous parameters?
    └─ SPACE-FILLING: Latin hypercube
```

## Core Capabilities

### 1. Randomization & Allocation

```python
# Permuted block randomization — keeps arms balanced throughout
import numpy as np

def block_randomization(n_total, arms, block_size=4, seed=42):
    """Generate randomized allocation schedule."""
    rng = np.random.default_rng(seed)
    schedule = []
    n_blocks = n_total // block_size
    for _ in range(n_blocks):
        block = arms * (block_size // len(arms))
        rng.shuffle(block)
        schedule.extend(block)
    return schedule

# Example: Randomize 16 simulation cases across 2 HPC batches
schedule = block_randomization(16, ["batch_A", "batch_B"], block_size=4, seed=42)
```

### 2. Full 2^k Factorial Design

Use when you have ≤5 factors and need all interactions.

```python
import itertools
import pandas as pd

def full_factorial(factors, seed=42):
    """Generate full 2^k factorial design matrix."""
    # factors: {"temp_C": (20, 60), "conc": (1, 10), ...}
    names = list(factors.keys())
    levels = [[-1, 1]] * len(names)
    design = pd.DataFrame(list(itertools.product(*levels)), columns=names)

    # Map coded levels to real units
    for name in names:
        low, high = factors[name]
        design[name] = design[name].map({-1: low, 1: high})

    # Randomize run order
    rng = np.random.default_rng(seed)
    design = design.iloc[rng.permutation(len(design))].reset_index(drop=True)
    return design

design = full_factorial({
    "breeder_thickness_cm": (3, 6),
    "Li6_enrichment_pct": (30, 90),
    "multiplier_thickness_cm": (1, 3)
})
```

### 3. Fractional Factorial — Screening Many Parameters

When you have >5 factors: `pyDOE3` generates resolution III/IV/V designs.

```python
# pip install pyDOE3
from pyDOE3 import fracfact

# 7 factors in 8 runs (Resolution III — main effects only)
design_coded = fracfact('a b c d e f g')
```

### 4. Central Composite Design — Response Surface with Curvature

```python
from pyDOE3 import ccdesign

# 3 factors: center + axial + factorial points
design_coded = ccdesign(3, center=(4, 4), face='ccc')

# Map to real units for breeder optimization
center = {"thickness": 4.5, "enrichment": 60, "temperature": 700}
steps = {"thickness": 0.5, "enrichment": 10, "temperature": 100}
```

### 5. Latin Hypercube — Space-Filling

```python
from pyDOE3 import lhs

# 50 design points in 4 dimensions
design = lhs(4, samples=50, criterion='maximin')

# Scale to real ranges
design[:, 0] = 3.0 + design[:, 0] * 3.0      # thickness: 3-6 cm
design[:, 1] = 30 + design[:, 1] * 60         # enrichment: 30-90%
design[:, 2] = 500 + design[:, 2] * 500       # temperature: 500-1000K
design[:, 3] = 0.5 + design[:, 3] * 2.5       # multiplier: 0.5-3.0 cm
```

## Nuclear Engineering Applications

### Scenario 1: Blanket TBR Optimization with Response Surface
Design a central composite experiment over 3 factors {breeder_thickness, Li-6 enrichment, multiplier_thickness} to find the TBR-maximizing combination, including quadratic curvature terms.

### Scenario 2: Shielding Material Screening with Plackett-Burman
Screen 7 candidate shielding materials (W, B4C, Pb, SS316, H2O, ZrH2, Polyethylene) for neutron attenuation effectiveness — only 8 runs instead of 128.

### Scenario 3: Latin Hypercube for Activation Cross-Section Sensitivity
Generate 100 Latin hypercube samples in {neutron energy, material composition, irradiation time} space to explore SDR sensitivity across operational envelopes.

### Scenario 4: Blocked Design for Code-to-Code Comparison
Randomize OpenMC vs MCNP runs in blocks by problem type (criticality, shielding, fusion) to avoid confounding code effect with problem complexity.

### Scenario 5: Sequential Design for On-Line Isotope Separation
Use adaptive design: initial fractional factorial → analyze → augment with follow-up runs near optimal region. Useful for expensive HPC simulations where each case costs hours.

## The Critical Mistakes That Ruin Simulation Studies

1. **Pseudoreplication.** Running 3 seeds on the same geometry is not 3 independent measurements — it's 1 design point with 3 seeds. Variance across seeds underestimates true design uncertainty.

2. **Confounding with run order.** Running all low-thickness cases on Monday and all high-thickness on Tuesday confounds thickness with machine state. **Randomize run order**.

3. **No blocking on HPC batch.** Different SLURM allocations can have different node hardware (CPU gen, memory speed). Block on HPC job ID.

4. **Aliasing in fractional designs.** A low-resolution screening design confounds main effects with interactions. Know your alias structure.

5. **Optimizing without curvature.** A 2^k factorial can't detect curved responses — you'll miss interior optima. Use response-surface designs when near an optimum.

## Installation

```bash
uv pip install numpy pandas pyDOE3
```

## Integration with Other Skills

- **parametric-sweep**: Use this skill to DESIGN the sweep matrix before generating input files
- **scikit-learn-ml**: Fit response-surface models to DOE results
- **matplotlib-seaborn-viz**: Visualize design matrices and response surfaces
- **polars-data**: Process DOE result tables at scale

## Best Practices

1. **Seed everything.** Record seeds for reproducibility — pre-register the design.
2. **Randomize run order**, not just parameter values.
3. Match the analysis to the design: blocks and strata must appear in the model.
4. For expensive HPC simulations: start with a fractional factorial, then augment.
5. Document the alias structure for fractional designs.

## Reference

- Montgomery, D. C. (2019). *Design and Analysis of Experiments* (10th ed.).
- Fisher, R. A. (1935). *The Design of Experiments*.
- For DOE with simulation codes: Santner, Williams & Notz (2018). *The Design and Analysis of Computer Experiments*.

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-07-13 | Initial creation — adapted from K-Dense-AI/scientific-agent-skills experimental-design skill, with nuclear engineering DOE scenarios | Agent science capability upgrade plan |
