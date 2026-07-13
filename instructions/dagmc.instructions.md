---
description: "DAGMC CAD-based Monte Carlo geometry: CAD-to-h5m workflow, OpenMC/MCNP integration, faceting pitfalls, and geometry validation checklist"
applyTo: ""
revision: 1
---

# DAGMC — Workflow & Validation Reference

Applicable versions: DAGMC ≥ 3.2 with OpenMC ≥ 0.14 or MCNP6.2+.

## WORKFLOW

### CAD-to-h5m Pipeline

1. **CAD preparation**: Clean geometry in CAD tool (STEP/SAT format). Ensure all volumes are closed solids, no overlapping bodies, no zero-thickness shells.
2. **Imprint & Merge**: In Cubit/Trelis, `imprint body all` then `merge body all` to share surfaces between adjacent volumes. **CRITICAL**: Skipping this step creates duplicate surfaces → geometry gaps → lost particles.
3. **Material group assignment**: Assign materials via groups:
   ```
   group "mat:Material_Name" add volume 1 2 3
   group "mat:Material_Name/rho:7.89" add volume 4  # with density override
   ```
   - Group naming is case-sensitive. Typos create unassigned volumes (silent error).
   - The `mat:` prefix is mandatory. The `rho:` suffix is optional (density can also come from the transport code material definition).
4. **Boundary conditions**:
   ```
   group "boundary:Reflecting" add surface 10 11
   group "boundary:Vacuum" add surface 20
   ```
5. **Faceting & Export**: `export dagmc "model.h5m"` with faceting tolerance.
   - Default tolerance: ~1e-3 cm. Tighter tolerance = more triangles = larger file = better geometry fidelity.
   - Typical range: 1e-4 (fine) to 1e-2 (coarse for scoping). Balance accuracy vs. file size.

### Faceting Tolerance Guidelines

| Model scale | Suggested tolerance | Expected .h5m size |
|-------------|--------------------|--------------------|
| Small (<1m) | 1e-4 cm | 10-100 MB |
| Medium (1-10m) | 1e-3 cm | 100 MB - 1 GB |
| Large (>10m) | 1e-2 cm (scoping) / 1e-3 cm (production) | 0.5 - 5 GB |

## INTEGRATION

### OpenMC Integration

```python
import openmc

dagmc_univ = openmc.DAGMCUniverse(filename='model.h5m', auto_geom_ids=True)
# For mixed CSG+DAGMC (overlay geometry):
cell = openmc.Cell(fill=dagmc_univ, region=-outer_sphere)
root = openmc.Universe(cells=[cell])
geometry = openmc.Geometry(root)
```

- `auto_geom_ids=True`: automatically assigns cell/surface IDs from the .h5m file.
- Material mapping: OpenMC maps DAGMC group names to `openmc.Material` objects by matching the `name` attribute.
- **Pitfall**: If `Material.name` doesn't match the DAGMC group `mat:XXX` string exactly, the volume gets no material (void) — **silent error**.

### MCNP Integration

DAGMC-MCNP uses the unstructured mesh (UM) capability:
- Requires DAGMC-enabled MCNP build
- Geometry specified via `DAGMC` keyword in input deck
- Material assignment through DAGMC groups (same convention as above)
- Performance note: DAGMC ray-tracing is typically 2-5× slower than native CSG for equivalent geometry complexity

## COMMON PITFALLS

### P1: Imprint/Merge Not Performed
**Symptom**: Lost particles near volume interfaces; particle tracks "teleport" between non-adjacent volumes.
**Cause**: Adjacent volumes don't share surfaces, creating infinitesimal gaps.
**Prevention**: Always run `imprint body all; merge body all` in Cubit before export. Verify merge count matches expected shared surfaces.

### P2: Group Name Typo → Silent Material Misassignment
**Symptom**: Unexpected void regions in areas that should have material; tally results in affected cells are wrong.
**Cause**: DAGMC group name (e.g., `mat:EUORFER` instead of `mat:EUROFER`) doesn't match any material definition in the transport code. The volume is silently treated as void.
**Prevention**: After loading geometry, programmatically verify all volumes have assigned materials:
```python
# OpenMC check
for cell in geometry.get_all_cells().values():
    if cell.fill is None:
        print(f"WARNING: Cell {cell.id} has no material!")
```

### P3: Faceting Tolerance Too Coarse
**Symptom**: Geometry artifacts — particles lost at curved surfaces, incorrect volume calculations.
**Cause**: Coarse faceting creates visible gaps between the faceted approximation and the true CAD surface.
**Prevention**: For production runs, use tolerance ≤1e-3 cm. Compare DAGMC volume calculations against CAD volumes — discrepancy >1% suggests tolerance is too coarse.

### P4: .h5m File Size → I/O Bottleneck
**Symptom**: Simulation startup takes minutes; HPC job aborts during geometry loading.
**Cause**: Fine faceting on large models produces multi-GB .h5m files that must be loaded into memory.
**Prevention**: Use coarser tolerance for scoping runs. On HPC, ensure sufficient memory per node. Consider extracting a simplified sub-geometry for local testing.

### P5: DAGMC "No Intersection" Warnings
**Symptom**: Progressive performance degradation during simulation; log filled with DAGMC warnings.
**Cause**: Ray-tracing encounters degenerate triangles or near-tangent surface intersections.
**Prevention**: Clean CAD geometry thoroughly — remove fillets/chamfers that are negligibly small relative to faceting tolerance. Filter warning output to prevent I/O bottleneck (redirect to `/dev/null` or grep-filter in wrapper script).

## VALIDATION CHECKLIST

After generating .h5m and before production run, verify:

- [ ] **Overlap check**: Run DAGMC overlap checker (`check_dagmc_overlaps` or equivalent). Zero overlaps required for production. Overlaps cause non-deterministic lost particles.
- [ ] **Volume comparison**: Compare DAGMC-computed volumes against CAD reference volumes. All cells within 1% for production; within 5% for scoping.
- [ ] **Material coverage**: Every volume in the .h5m has a corresponding material group assignment. No unassigned volumes (check transport code warnings at startup).
- [ ] **Material name matching**: All DAGMC `mat:XXX` group names match transport code material definitions exactly (case-sensitive).
- [ ] **Boundary conditions**: Reflecting/vacuum surfaces are correctly assigned. Verify with a low-particle visual inspection run.
- [ ] **Lost particles**: Run a quick 1000-particle test. Zero lost particles expected. If any occur, investigate geometry gaps near reported coordinates.
- [ ] **File size sanity**: .h5m file size is within expected range for model complexity and tolerance (see table above).
