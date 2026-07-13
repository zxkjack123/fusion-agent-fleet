---
description: "scnetresource-router HPC resource margin policy: wall time, CPU, memory safety multipliers to prevent job failures from insufficient resource requests"
applyTo: "fusion-deep-research,scnet-hpc-coordinator,simulation-analyst,simulation-builder,task-executor"
revision: 3
---

# scnetresource-router Resource Margin Policy

When submitting HPC jobs via `scnetresource-router/*`, apply the following safety margins to prevent job failures from insufficient resource requests. Failed jobs waste queue wait time and all consumed SUs.

## Wall-Time Safety

- **Multiply estimated wall time by 2.5×** before setting it in `requirements.wall_time`.
- Set a **minimum floor of 24 hours** regardless of estimated duration. Repeated job timeouts waste far more time than generous wall-time requests; SLURM only charges for actual usage.
- Present both the raw estimate and the padded value to the user before submission.
- For first-time runs on unfamiliar models/clusters, use **3×** multiplier.

## CPU Core Safety

- **Default to multi-node allocation** for parallel transport codes (OpenMC, MCNP): request **at least 2 full nodes** (typically 64–128 cores total depending on cluster). The user's time is far more valuable than idle SUs — do not be conservative with node count.
- For production runs or any job expected to run >1 hour: prefer **4+ nodes** unless the problem is known to be small. Parallel efficiency on well-scaling transport codes (OpenMC, MCNP) remains good up to hundreds of cores.
- For memory-intensive tasks (DAGMC geometry, large tally meshes, activation inventory): prefer **exclusive node allocation** if the scheduler supports it.
- When unsure about optimal parallelism, **first run a short scaling test** (e.g., 100 batches on 1, 2, 4 nodes) to find the sweet spot, then submit the full production run at the optimal node count. This is faster overall than guessing conservatively.
- Never request a partial node for MPI-parallel codes — always request full exclusive nodes to avoid memory contention from co-located jobs.

## Memory Safety

- If `requirements` supports a memory field, request **1.5× the estimated peak memory**.
- DAGMC-based models can spike to 2–4 GB/process; account for this when calculating total memory per node.
- FISPACT-II inventory calculations are lightweight per-process but can be numerous in R2S workflows; ensure total node memory covers all concurrent instances.

## Estimation Heuristics for Nuclear Simulations

| Workload | Typical wall time (per run) | Recommended nodes | Recommended wall time |
|----------|-----------------------------|--------------------|----------------------|
| OpenMC eigenvalue (≤1M particles, simple geometry) | 5–30 min | 2 nodes | 24 h (min floor) |
| OpenMC eigenvalue (>10M particles or DAGMC) | 30 min – 4 h | 4+ nodes | 2.5× estimate, min 24 h |
| OpenMC fixed-source (mesh tallies) | 1–8 h | 4+ nodes | 2.5× estimate, min 24 h |
| MCNP6 (similar complexity to above) | similar | similar | similar |
| FISPACT-II single irradiation | seconds – 2 min | 1 node | 24 h (batch overhead) |
| natf R2S coupled workflow | 2–12 h | 4+ nodes | 3× estimate, min 24 h |

## Pre-Submission Checklist

Before calling `task_run_auto(..., dry_run=false, confirm=true)`:

1. ✅ Wall time has safety multiplier applied (≥2.5×, floor ≥24 h)
2. ✅ CPU nodes are generous (≥2 nodes for parallel codes, ≥4 for production runs)
3. ✅ `dry_run=true` preview has been presented to user
4. ✅ User has explicitly confirmed submission
5. ✅ `task_id` will be recorded for monitoring
