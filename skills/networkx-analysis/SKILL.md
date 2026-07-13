---
name: networkx-analysis
description: "Graph/network analysis for nuclear engineering — nuclide decay chain visualization, nuclear data dependency graphs, simulation workflow DAGs. Use when: decay chain mapping, nuclear reaction network analysis, Monte Carlo particle tracking graph, computational workflow optimization. 图/网络分析：核素衰变链可视化、核数据依赖图、仿真工作流DAG。"
revision: 1
---

# NetworkX — Graph Analysis for Nuclear Engineering

## When to Use

- Visualizing nuclide decay chains and reaction networks
- Mapping nuclear data library dependencies (ENDF → ACE → HDF5)
- Analyzing simulation workflow DAGs for optimization
- Building material composition dependency graphs
- Shortest-path analysis in burnup/depletion networks
- Community detection in isotope co-occurrence data

## When NOT to Use

- For general statistical data analysis — use `data-analyst` agent
- For very large graphs (>1M nodes) — consider igraph or graph-tool
- For molecular graph neural networks — use `deepchem-ml` skill
- For TikZ-quality graph diagrams — use `tikz-writer` MCP

## Core Capabilities

### 1. Graph Construction

```python
import networkx as nx

# Directed graph for decay chains
G = nx.DiGraph()

# Add nodes with metadata
G.add_node("Co-60", half_life=5.27, unit="years", decay_mode="beta-")
G.add_node("Ni-60", half_life="stable")

# Add edges with transition data
G.add_edge("Co-60", "Ni-60", probability=1.0, q_value=2.824, unit="MeV")
```

### 2. Centrality Analysis

```python
# Find most connected nuclides (hub nodes in decay networks)
betweenness = nx.betweenness_centrality(G)
top_hubs = sorted(betweenness.items(), key=lambda x: -x[1])[:10]

# PageRank for importance ranking
pagerank = nx.pagerank(G)
```

### 3. Path Analysis — Decay Chain Tracing

```python
# Find all decay paths from parent to stable daughter
paths = list(nx.all_simple_paths(G, "U-238", "Pb-206", cutoff=20))
for i, path in enumerate(paths[:5]):
    print(f"Path {i}: {' → '.join(path)} (length: {len(path)-1} decays)")
```

### 4. Community Detection

```python
from networkx.algorithms.community import greedy_modularity_communities

# Group nuclides by decay families
communities = list(greedy_modularity_communities(G))
for i, comm in enumerate(communities):
    print(f"Community {i}: {len(comm)} nuclides — {list(comm)[:5]}...")
```

### 5. Visualization

```python
import matplotlib.pyplot as plt

pos = nx.spring_layout(G, k=2, seed=42)
nx.draw(G, pos, with_labels=True, node_color='lightblue',
        node_size=800, font_size=8, arrowsize=10)
plt.title("Activation Product Decay Network")
```

### 6. Workflow DAG Analysis

```python
# Simulation workflow as DAG
W = nx.DiGraph()
W.add_edges_from([
    ("Geometry", "Transport"),
    ("Materials", "Transport"),
    ("Transport", "Tally"),
    ("Tally", "Activation"),
    ("Activation", "Dose"),
])

# Critical path
critical = nx.dag_longest_path(W)
print(f"Critical path: {' → '.join(critical)}")

# Topological sort for execution order
order = list(nx.topological_sort(W))
print(f"Execution order: {order}")
```

## Nuclear Engineering Applications

### Scenario 1: Nuclide Decay Chain Visualization
Build a directed graph from FISPACT-II inventory output, with nodes = nuclides (color-coded by half-life) and edges = decay modes (beta-/beta+/alpha/IT). Trace dominant decay pathways from activated parents to stable daughters.

### Scenario 2: Nuclear Data Dependency Graph
Map ENDF/B → NJOY → ACE → HDF5 → OpenMC data pipeline as a DAG. Identify critical nodes where library format changes could break downstream codes.

### Scenario 3: Monte Carlo Particle Ancestry
Track neutron birth → scattering → absorption/leakage as a tree graph. Analyze branch depth distribution to optimize variance reduction parameters.

### Scenario 4: Cross-Section Resonance Network
For resolved resonance region, build a bipartite graph: isotopes ↔ energy levels, with edge weights = resonance integrals. Cluster isotopes with similar resonance structures.

### Scenario 5: Supply Chain Analysis for Fusion Materials
Build a directed graph of rare isotope production pathways (Li-6 enrichment, Be purification, Pb-Li synthesis) — identify single-point dependencies.

## Integration with Other Skills

- **polars-data**: Load large decay chain data tables, then convert to NetworkX graph
- **matplotlib-seaborn-viz**: Visualize the graph with publication-quality rendering
- **experimental-design**: Model experiment factor interactions as graph structures

## Installation

```bash
uv pip install networkx matplotlib
```

## Best Practices

1. Use `nx.DiGraph` for directed processes (decay, workflows); `nx.Graph` for symmetric relationships
2. Store metadata as node/edge attributes, not in node names
3. For large graphs (>10K nodes), prefer `spring_layout` with `k` tuning over `kamada_kawai`
4. Cache centrality computations — they are O(n²) or worse
5. Validate decay chain graphs against NUBASE/ENSDF data for physical correctness

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-07-13 | Initial creation — adapted from K-Dense-AI/scientific-agent-skills networkx skill, with nuclear engineering graph analysis scenarios | Agent science capability upgrade plan |
