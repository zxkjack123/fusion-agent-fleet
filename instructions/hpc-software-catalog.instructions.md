---
description: "HPC software catalog lookup policy: agents MUST consult software catalog via MCP tools (software_list / software_resolve) before launching any simulation on any cluster. 集群软件部署查询策略, MCNP/OpenMC/FISPACT/natf/ALARA/PyNE 多集群部署配置, 避免重复踩坑."
applyTo: "fusion-deep-research,scnet-hpc-coordinator,simulation-analyst,simulation-builder,task-executor"
revision: 2
---

# HPC Software Catalog Policy — 集群软件部署查询策略

## Core Rule

**Before launching ANY simulation software (MCNP6, OpenMC, FISPACT-II, natf, ALARA, PyNE) on ANY HPC cluster, the agent MUST consult the software catalog to determine the correct deployment method.**

The software catalog is accessed via `scnetresource-router` MCP tools — **NOT** by reading a static YAML file or searching the filesystem.

## Lookup Procedure

1. **Query availability**: `software_list(software="mcnp6")` → returns which clusters have it registered, with runtime/variant info
2. **Resolve details**: `software_resolve(cluster="sugon_hb", software="mcnp6")` → returns full deployment config (runtime, image, binary, mpi_launch, env)
3. **Check `runtime` field**:
   - `apptainer` → container execution with specified `image`
   - `host` → native binary execution with specified `binary` and `env`
   - Not found / `not_configured` → **STOP**, report to user that software is not available on this cluster
4. **Submit via software parameter**: `task_run_auto(software="mcnp6", ...)` — the `software` parameter auto-resolves the profile; do NOT manually construct container/binary launch commands
5. **Respect `mpi_launch`** from the resolved config (srun --mpi=pmix vs srun --mpi=pmi2)

**NEVER** use `remote_find` / `remote_ls` to search for software binaries on cluster filesystems. The MCP software catalog is the single source of truth.

### Fallback: Static catalog YAML

If `software_list` / `software_resolve` MCP tools are unavailable (MCP server not connected), fall back to reading `instructions/hpc-software-catalog.yaml` (relative to this file). The YAML file may be stale — prefer MCP tools when available.

## Critical Constraints

| Cluster | MPI launcher | Why |
|---------|-------------|-----|
| sugon_hb | `srun --mpi=pmix` | OpenMPI in container uses PMIx |
| kunshan | `srun --mpi=pmi2` | MPICH uses PMI2; PMIx incompatible |
| xian | — | MCNP6 unavailable |

**NEVER mix these up.** Using `--mpi=pmix` on kunshan or `--mpi=pmi2` on sugon_hb will cause silent failures (processes start but can't communicate).

## When Catalog Entry is Missing

If the target (cluster, software) pair has no entry or `software_resolve` returns `not_configured`:

1. **Do NOT guess** the deployment method
2. **Do NOT search the filesystem** with `remote_find` / `remote_ls`
3. Report to user: "Software X is not yet configured for cluster Y. Catalog entry missing."
4. Suggest using `software_register` (via Scnet HPC Coordinator delegation) to register the deployment

## When to Update the Catalog

Update the software catalog via `software_register` (delegated to Scnet HPC Coordinator) after:
- Successfully validating a new software deployment on a cluster
- Discovering that a previously working deployment is broken
- Adding a new cluster to the pool

## Integration with Scnet HPC Coordinator

When Scnet HPC Coordinator selects a cluster for job submission:
1. Coordinator calls `choose_best` or equivalent to pick cluster
2. **Before generating the job script**, call `software_resolve(cluster=..., software=...)` to get deployment config
3. Pass the `software` parameter to `task_run_auto` — the server handles profile resolution automatically
4. If `software_resolve` returns `not_configured`, Coordinator must pick the next-best cluster

## User-Mentioned Software Rule

When the user states that a specific software is available on a cluster (e.g., "曙光上有编译好的 MCNP"):

1. **Verify first**: Call `software_list(software="mcnp6")` to check if it is already registered in the catalog
2. **If registered** → use `task_run_auto(software="mcnp6", ...)` directly; do NOT search the filesystem
3. **If NOT registered** → ask the user for deployment details (binary path, container image, runtime type) and propose `software_register` via Scnet HPC Coordinator delegation
4. **NEVER** treat user's statement as license to `remote_find` across the filesystem

## Relationship to Other Instructions

- `instructions/mcnp6.instructions.md` → MCNP6 input format rules (software-agnostic)
- `instructions/hpc-ssh-routing.instructions.md` → How to reach clusters
- `instructions/scnetresource-router.instructions.md` → Resource margins
- **This file** → Which binary/container to use on which cluster

## Quick Reference Table

| Cluster | MCNP6 | OpenMC | FISPACT | natf | ALARA |
|---------|--------|--------|---------|------|-------|
| sugon_hb | ✅ SIF | ❓ | ❓ | ❓ | ❓ |
| kunshan | ✅ native Intel | ❓ | ❓ | ❓ | ❓ |
| xian | ❌ | ❓ | ❓ | ❓ | ❓ |

Legend: ✅ validated, ❓ not yet configured, ❌ confirmed unavailable
