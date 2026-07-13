---
name: pymatgen-materials
description: "Materials science toolkit for nuclear engineering — crystal structures (CIF, POSCAR), phase diagrams, band structure, DOS, Materials Project integration, format conversion. Use when: computational materials science, nuclear material screening, irradiation damage pre-processing, first-wall/blanket material thermodynamics. 材料科学工具包：晶体结构、相图、能带、Materials Project 集成、核材料筛选。"
revision: 1
---

# Pymatgen — Materials Science Toolkit for Nuclear Engineering

## When to Use

- Working with crystal structures or molecular systems in materials science
- Converting between structure file formats (CIF, POSCAR, XYZ, etc.)
- Analyzing symmetry, space groups, or coordination environments
- Computing phase diagrams or assessing thermodynamic stability
- Analyzing electronic structure data (band gaps, DOS, band structures)
- Accessing the Materials Project database for material property screening
- Setting up DFT calculation inputs (VASP, Quantum ESPRESSO) for nuclear materials

## When NOT to Use

- For direct OpenMC/MCNP material card generation — use `simulation-builder` agent or `openmc-validator/get_material_tool`
- For FISPACT-II inventory specification — use `fispact-lint/check_material`
- For nuclear data (cross-sections, decay data) — use `nuclear-data-mcp` tools
- For literature review of nuclear materials — use `scientific-paper-research` agent

## Core Capabilities

### 1. Structure Creation and Manipulation

```python
from pymatgen.core import Structure, Lattice

# Read structure from file (automatic format detection)
struct = Structure.from_file("POSCAR")
struct = Structure.from_file("structure.cif")

# Create from space group
struct = Structure.from_spacegroup("Fm-3m", Lattice.cubic(3.5), ["Si"], [[0,0,0]])

# Get properties
print(f"Formula: {struct.composition.reduced_formula}")
print(f"Space group: {struct.get_space_group_info()}")
print(f"Density: {struct.density:.2f} g/cm³")
```

### 2. Materials Project Database Access

```python
from mp_api.client import MPRester

with MPRester() as mpr:
    # Search for nuclear-relevant materials
    materials = mpr.materials.summary.search(
        chemsys="Li-Si-O",            # Li4SiO4 breeder system
        energy_above_hull=(0, 0.05),  # Stable/metastable
    )
    struct = mpr.get_structure_by_material_id("mp-149")
```

### 3. Phase Diagrams and Thermodynamics

```python
from pymatgen.analysis.phase_diagram import PhaseDiagram

# Construct phase diagram for breeder/multiplier systems
entries = mpr.get_entries_in_chemsys("Li-Pb")  # LiPb breeder
pd = PhaseDiagram(entries)
decomp = pd.get_decomposition(Composition("LiPb"))
```

### 4. Electronic Structure Analysis

Band structures, DOS, and electronic properties for radiation damage understanding.

### 5. Surface and Interface Analysis

Slab generation, adsorption site finding — relevant for plasma-facing component (PFC) surface studies.

## Nuclear Engineering Applications

### Scenario 1: Fusion Breeder Material Screening
Use Materials Project API to screen Li-ceramic breeder candidates (Li4SiO4, Li2TiO3, Li2ZrO3) for thermal stability, phase purity, and Li density.

### Scenario 2: First-Wall Material Thermodynamics
Compare reduced-activation ferritic/martensitic (RAFM) steel constituent phases via phase diagrams — predict precipitate formation under irradiation.

### Scenario 3: Tritium Permeation Barrier Candidates
Search for dense ceramic coatings (Al2O3, Er2O3, Cr2O3) with high melting points and chemical compatibility with EUROFER/RAFM.

### Scenario 4: Neutron Multiplier Screening
Evaluate Be and Be-alloy phase stability; compute BeO formation enthalpy under accident conditions.

## Installation

```bash
uv pip install pymatgen mp-api
```

Materials Project API key: `export MP_API_KEY="your_key"` from https://next-gen.materialsproject.org/

## Integration with Other Skills

- **parametric-sweep**: Use pymatgen to parameterize material compositions for OpenMC/FISPACT sweeps
- **fusion-magnet-heating-normalization**: Cross-check material thermal limits with phase stability
- **experimental-design**: Design composition screening experiments

## Best Practices

1. Use `Structure.from_file()` with automatic format detection
2. Prefer `MPRelaxSet` over manual INCAR generation for VASP
3. Cache Materials Project results locally for reproducibility
4. Check symmetry with `SpacegroupAnalyzer` before supercell generation
5. Validate structures for overlapping atoms or unreasonable bond lengths

## Revision Log

| Rev | Date | Change | Source |
|-----|------|--------|--------|
| 1 | 2026-07-13 | Initial creation — adapted from K-Dense-AI/scientific-agent-skills pymatgen skill, with nuclear engineering focus | Agent science capability upgrade plan |
