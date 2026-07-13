---
name: matplotlib-seaborn-viz
description: "Publication-grade scientific visualization for nuclear engineering — line plots, scatter plots, bar charts, heatmaps, 3D plots, neutron energy spectra, TBR sensitivity charts, activation time-evolution plots. Use when: creating figures for papers/reports/presentations from simulation or experimental data. 出版级科研可视化：中子能谱、TBR灵敏度图、活化产物时间演化图。"
revision: 1
---

# Matplotlib & Seaborn — Scientific Visualization for Nuclear Engineering

## When to Use

- Creating publication-quality figures for papers, reports, or presentations
- Visualizing simulation results (TBR, keff, neutron spectra, DPA, SDR)
- Making sensitivity analysis charts (tornado plots, response surfaces)
- Time-series plots for activation/decay chains
- Comparative plots: simulation vs experiment, code vs code
- Multi-panel figures for journal submissions

## When NOT to Use

- For programmatic TikZ diagrams (flowcharts, schematics) — use `tikz-writer` MCP or `diagram-architect` agent
- For AI-generated methodology diagrams — use PaperBanana CLI (`paperbanana generate`)
- For interactive dashboards — use Plotly or Streamlit
- For very large datasets (>1M points) — downsample first

## Core Capabilities

### 1. Publication-Ready Figure Template

```python
import matplotlib.pyplot as plt
import seaborn as sns

# NeurIPS/IEEE-compatible style
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

fig, ax = plt.subplots(figsize=(3.5, 2.5))  # Single-column width
ax.plot(x, y, 'o-', markersize=3, linewidth=1.2, label='Data')
ax.set_xlabel('Energy (MeV)')
ax.set_ylabel('Flux (n/cm²/s)')
ax.legend(frameon=False)
ax.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig('figure.pdf', format='pdf')
```

### 2. Neutron Energy Spectrum (with error bands)

```python
fig, ax = plt.subplots(figsize=(5, 3))
ax.errorbar(energy_bins, flux, yerr=flux_err, fmt='o-', capsize=2,
            markersize=3, linewidth=1.0, label='Flux spectrum')
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel('Energy (MeV)'); ax.set_ylabel('Flux (n/cm²/s per MeV)')
```

### 3. TBR Sensitivity Tornado Chart

```python
import numpy as np

params = ['Li-6 Enrich.', 'Breeder Thick.', 'FW Thick.', 'Multiplier Thick.']
delta_tbr = [0.08, 0.12, -0.03, 0.05]  # ΔTBR from perturbation

fig, ax = plt.subplots(figsize=(4, 3))
colors = ['#2ca02c' if v > 0 else '#d62728' for v in delta_tbr]
ax.barh(params, delta_tbr, color=colors, height=0.6)
ax.axvline(0, color='black', linewidth=0.8)
ax.set_xlabel('ΔTBR')
```

### 4. Activation Decay Heat Time Series

```python
fig, ax = plt.subplots(figsize=(5, 3))
for isotope, data in decay_curves.items():
    ax.loglog(data['time'], data['activity'], label=isotope, linewidth=1.2)
ax.set_xlabel('Cooling time (s)'); ax.set_ylabel('Activity (Bq)')
ax.legend(ncol=2, fontsize=8)
```

### 5. Heatmaps for 2D Parameter Sweeps

```python
# TBR vs (breeder_thickness, Li6_enrichment)
fig, ax = plt.subplots(figsize=(4, 3))
im = ax.contourf(X_grid, Y_grid, Z_grid, levels=15, cmap='viridis')
plt.colorbar(im, ax=ax, label='TBR')
ax.set_xlabel('Breeder Thickness (cm)'); ax.set_ylabel('Li-6 Enrichment (%)')
```

### 6. Comparative Bar Charts (Code vs Experiment)

```python
fig, ax = plt.subplots(figsize=(5, 3))
x = np.arange(len(benchmarks)); width = 0.35
ax.bar(x - width/2, exp_values, width, label='Experiment', color='#1f77b4')
ax.bar(x + width/2, sim_values, width, label='OpenMC', color='#ff7f0e')
ax.set_xticks(x); ax.set_xticklabels(bench_names)
ax.legend()
```

## Nuclear Engineering Applications

### Scenario 1: Neutron Flux Spectrum from OpenMC Tally
Plot multi-group flux with error bands from `openmc-validator/extract_tally_summary_tool` output. Overlay with reference spectrum (e.g., FENDL, JEFF).

### Scenario 2: TBR Sensitivity Analysis
Generate tornado chart showing ΔTBR per 1% parameter perturbation across breeder, multiplier, and structural dimensions from a parametric sweep.

### Scenario 3: Activation Product Dominance Plot
Semi-log bar chart of top 20 activation products by activity at shutdown, grouped by element, from FISPACT-II output.

### Scenario 4: SDR Decay Profile
Dual-axis plot: decay heat (W) and contact dose rate (Sv/h) vs cooling time, with regulatory limit reference lines.

### Scenario 5: Multi-Model Comparison
Overlay TBR values from multiple design iterations or different codes (OpenMC vs MCNP) with uncertainty bars.

## Color Schemes

### Recommended Palettes for Nuclear Engineering

```python
# Neutron energy: sequential blue
cmap_neutron = plt.cm.Blues

# Temperature/Dose: sequential red-orange
cmap_thermal = plt.cm.YlOrRd

# Material comparison: qualitative Set2
cmap_materials = sns.color_palette("Set2", n_colors=8)

# Diverging for ΔTBR: RdBu
cmap_diverging = plt.cm.RdBu_r
```

## Installation

```bash
uv pip install matplotlib seaborn numpy pandas
```

Standard in all scientific Python environments.

## Integration with Other Skills

- **data-analyst agent**: Delegate complex multi-panel figure generation
- **parametric-sweep**: Post-sweep visualization pipeline
- **manuscript-figure-package-rebuild**: Ensure units/colorbar alignment with manuscript text

## Best Practices

1. Use vector formats (PDF/SVG) for journal submissions; PNG for quick previews
2. Set `figsize` to match target journal column width (e.g., 3.5in for single-col)
3. Always include error bars/uncertainty bands for nuclear data
4. Use log scale for neutron energy spectra (9 decades typical)
5. Colorblind-friendly palettes: `sns.color_palette("colorblind")`
6. LaTeX rendering for axis labels: `plt.rcParams['text.usetex'] = True`

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-07-13 | Initial creation — adapted from K-Dense-AI/scientific-agent-skills matplotlib/seaborn skills, with nuclear engineering visualization recipes | Agent science capability upgrade plan |
