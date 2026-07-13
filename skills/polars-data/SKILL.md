---
name: polars-data
description: "High-performance data processing for nuclear engineering — expression-based DataFrame manipulation, lazy evaluation, Arrow interoperability, large-scale tally data processing, nuclear database batch queries, Monte Carlo result aggregation. Use when: handling >1M rows of simulation output, streaming CSV/Parquet from HPC, pandas migration for nuclear datasets. 高性能数据处理：大规模tally数据处理、核数据库批量查询、蒙特卡洛结果聚合。"
revision: 1
---

# Polars — High-Performance Data Processing for Nuclear Engineering

## When to Use

- Processing large Monte Carlo tally outputs (>1M rows)
- Aggregating parametric sweep results across hundreds of cases
- Streaming large CSV/Parquet files from HPC downloads
- Batch querying nuclear databases with complex filters
- Replacing slow pandas pipelines with expression-based Polars
- Arrow-based interoperability with OpenMC/PyNE data structures

## When NOT to Use

- For interactive exploratory analysis on small data (<10K rows) — pandas is fine
- For GPU-accelerated computation — use CuDF or RAPIDS
- For image or signal processing — use NumPy/SciPy directly
- For statistical modeling — load into `scikit-learn-ml` after Polars ETL

## Core Capabilities

### 1. Expression-Based API

```python
import polars as pl

df = pl.DataFrame({
    "case_id": range(1000),
    "breeder_thickness": [3.5 + i*0.01 for i in range(1000)],
    "li6_enrichment": [30 + (i % 5)*5 for i in range(1000)],
    "tbr": [1.05 + 0.001*i for i in range(1000)],
    "tbr_std": [0.005]*1000,
})

# Filter + compute in one expression chain
result = (
    df.filter(pl.col("tbr") > 1.10)
      .with_columns(tbr_over_threshold=pl.col("tbr") - 1.10)
      .group_by("li6_enrichment")
      .agg(pl.col("tbr").mean().alias("mean_tbr"),
           pl.col("tbr").std().alias("std_tbr"),
           pl.len().alias("n_cases"))
      .sort("li6_enrichment")
)
```

### 2. Lazy Evaluation — Essential for Large Files

```python
# Scan CSV without loading into memory
lf = pl.scan_csv("sweep_results.csv")

result = (
    lf.filter(pl.col("tbr_rel_err") < 0.05)  # Filter unconverged
      .select(["case_id", "breeder_thickness", "li6_enrichment", "tbr"])
      .collect()  # Execute optimized query once
)
```

### 3. Pandas Migration — Key Mappings

| Operation | Pandas | Polars |
|-----------|--------|--------|
| Select column | `df["col"]` | `df.select("col")` |
| Filter | `df[df["col"] > 10]` | `df.filter(pl.col("col") > 10)` |
| Add column | `df.assign(x=...)` | `df.with_columns(x=...)` |
| Group by | `df.groupby("col").mean()` | `df.group_by("col").agg(pl.col("val").mean())` |
| Window | `df.groupby("col").transform(...)` | `pl.col("val").mean().over("col")` |

### 4. Pattern: TBR Results Aggregation with Uncertainty Filtering

```python
# Read HPC sweep output
df = pl.read_csv("sweep/all_results.csv")

# Filter statistically significant results
df_clean = (
    df.filter(
        pl.col("tbr_rel_err") < 0.03,  # < 3% relative error
        pl.col("tbr") > 0.5,           # Physically plausible
    )
)

# Pivot for 2D visualization
pivot = df_clean.pivot(
    on="li6_enrichment",
    values="tbr",
    index="breeder_thickness"
)
```

### 5. Pattern: Parquet I/O for Large Nuclear Datasets

```python
# Save (fast binary format with compression)
df.write_parquet("sweep.parquet", compression="zstd")

# Load lazy — reads only needed columns
lf = pl.scan_parquet("sweep*.parquet")  # Glob for multi-file
result = lf.select(["case_id", "tbr"]).filter(pl.col("tbr") > 1.0).collect()
```

## Nuclear Engineering Applications

### Scenario 1: OpenMC Tally Aggregation
Read multi-case tally CSV output, filter by relative error < 5%, compute mean and std TBR per parameter combination.

### Scenario 2: FISPACT Inventory Processing
Load gigabyte-scale `.out` files parsed to tabular format. Filter dominant nuclides (>1% activity), group by element, pivot for time-series comparison.

### Scenario 3: Cross-Code Benchmark Comparison
Join OpenMC results CSV with MCNP output CSV on shared case ID, compute C/E ratios with statistical tests.

### Scenario 4: Nuclear Data Library Audit
Batch-query `nuclear-data-mcp` for all isotopes in a material specification, join with library availability check, flag missing cross-section data.

### Scenario 5: Parametric Sweep Post-Processing
Load hundreds of sweep case CSVs, merge into single DataFrame, compute sensitivity indices (∂TBR/∂param), export to `matplotlib-seaborn-viz` for tornado plotting.

## Installation

```bash
uv pip install polars
# Optional: Excel, database, cloud, pandas interop
uv pip install 'polars[excel,database,fsspec,pandas]'
```

## Integration with Other Skills

- **scikit-learn-ml**: Use Polars for ETL → convert to NumPy for sklearn
- **matplotlib-seaborn-viz**: Aggregate data with Polars → visualize
- **parametric-sweep**: Post-process sweep results with lazy Polars pipelines

## Best Practices

1. **Use lazy evaluation** (`scan_csv`/`scan_parquet`) for files > 100 MB
2. Select only needed columns early — Polars pushes projections down
3. For streaming: `lf.collect(engine="streaming")` on very large datasets
4. Prefer expression API over `.map_elements()` — the latter breaks parallelization
5. Embed physical unit checks: `.filter(pl.col("tbr").is_between(0.5, 2.5))`

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-07-13 | Initial creation — adapted from K-Dense-AI/scientific-agent-skills polars skill, with nuclear data processing patterns | Agent science capability upgrade plan |
