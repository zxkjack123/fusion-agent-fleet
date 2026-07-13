---
name: parametric-sweep
description: "Design and execute parameter sweep matrices for fusion simulation codes (OpenMC/MCNP/FISPACT). Generates sweep matrix, submits batch HPC jobs, aggregates results. Use when: parameter scan, sensitivity analysis, design space exploration, optimization study, 扫描, 参数化, 灵敏度分析, 设计空间探索."
revision: 1
---

# Parametric Sweep Automation

## When to Use

- Need to run the same simulation with varying parameters (thickness, composition, temperature, etc.)
- Sensitivity analysis: identify which parameters most affect the output
- Design optimization: find optimal parameter combination
- Design space exploration: map the response surface

## When NOT to Use

- Single simulation run (use fusion-chain-runner directly)
- Code development or debugging (use simulation-builder)
- Post-processing existing results (use simulation-analyst)
- Only 1-2 parameter variations (just run manually)

## Workflow

### Stage A: Parameter Matrix Design

1. **Identify sweep parameters** from user's request:
   - Parameter name (e.g., `breeder_thickness`, `Li6_enrichment`, `FW_thickness`)
   - Range: `[min, max]` or explicit values `[v1, v2, v3, ...]`
   - Step size (for range) or explicit list
   - Dependencies: independent vs coupled parameters

2. **Generate sweep matrix**:
   - For independent parameters: full factorial (all combinations)
   - For coupled parameters: user-specified pairs
   - Output a CSV table: each row = one simulation case, each column = one parameter
   - Calculate total number of cases — **WARN if > 100 cases** (HPC queue limit)

3. **Parameterize input deck**:
   - Identify which lines in the input file(s) correspond to each parameter
   - Create a template with `{{param_name}}` placeholders
   - Validate template by rendering one case and checking with `openmc-validator/validate_model_tool` or `fispact-lint/full_scan`

### Stage B: Batch Submission

1. **Generate per-case input files**:
   - One directory per case: `sweep/case_001/`, `sweep/case_002/`, ...
   - Each directory contains the rendered input file(s)
   - Write `sweep_matrix.csv` at the top level with all case parameters

2. **Submit to HPC**:
   - If OpenMC: use `scnetresource-router/fusion_openmc_run` per case, or
   - Use `scnetresource-router/task_run_array_auto` with commands list (one per case)
   - If MCNP: use `skills/sugon-mcnp6-apptainer` sbatch template, one per case
   - Record all `task_id`s in `sweep/manifest.json`

3. **Monitor**:
   - Use `scnetresource-router/task_array_status` to check all cases
   - Use `scnetresource-router/task_array_retry_failed` for failed cases
   - **Target: all cases COMPLETED before Stage C**

### Stage C: Result Aggregation

1. **Download and parse results**:
   - Use `scnetresource-router/task_array_download` to fetch all outputs
   - For OpenMC: use `openmc-validator/extract_tally_summary_tool` per case
   - For FISPACT: use `scnetresource-router/fusion_parse` per case
   - For MCNP: parse `outp` files manually or with `simulation-analyst`

2. **Build results table**:
   - Append output columns to `sweep_matrix.csv`:
     `case_id, param1, param2, ..., result1, result2, uncertainty1, ...`
   - Save as `sweep/results.csv`

3. **Generate summary plots**:
   - Delegate to `data-analyst` or `simulation-analyst` with the results CSV
   - Request: sensitivity tornado chart, response surface (if 2 params), trend plots
   - Save figures to `sweep/figures/`

4. **Version management**:
   - Call `project-management/pm_asset_snapshot` with `include_content=true` for `sweep/results.csv`
   - Call `project-management/pm_asset_mark_important` for the results CSV
   - Commit `sweep/` directory to git if in a project repo

## Common Pitfalls

- **HPC queue limit**: SCNet typically allows 50-100 concurrent jobs. If sweep has >100 cases, split into batches.
- **Parameter validation**: Always validate one rendered input before batch submission — a template error wastes all HPC time.
- **Disk space**: MCNP/OpenMC output files can be 1-10 GB per case. Check disk quota before starting large sweeps.
- **Normalization**: Ensure all cases use the same source strength and normalization convention — otherwise results are not comparable.
- **Statistical convergence**: OpenMC/MCNP results with relative error >5% are unreliable for sweep comparison. Filter or re-run high-error cases.

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-06-24 | Initial creation | Research lifecycle gap analysis |
