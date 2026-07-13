---
description: "When to use OpenMC Plotter for geometry verification before HPC submission. OpenMC-plotter 几何验证：在 HPC 提交前用 batch mode 验证 DAGMC 几何切片。"
applyTo: "**"
version: 1
revision: 1
---

# OpenMC Plotter Verification — 几何可视化验证

## When to Use

- Before HPC submission of DAGMC-based OpenMC models — verify geometry slices
- When debugging geometry overlaps or material assignment issues
- When verifying source site distributions

## When NOT to Use

- CSG geometry — use `openmc-validator/validate_geometry` instead (already in simulation-builder Stage E)
- Production visualization — use ParaView or Visit for published figures

## Workflow

1. **Install**: `pip install openmc-plotter` (one-time)
2. **Save view**: In GUI mode, create a view file: `openmc-plotter <model_dir>` → File → Save View Settings → `check.pltvw`
3. **Batch mode**: `openmc-plotter -b check.pltvw` — generates image without GUI
4. **Verify**: Check output image for:
   - Overlay regions (colored overlap = geometry bug)
   - Correct material assignments (color by material)
   - Source site positions (if using external source)

## Fallback

If openmc-plotter is not installed: `openmc-validator/validate_geometry` with `geometry_debug=True` flag.

## Integration

- `simulation-builder` Stage E (Validation & Pre-flight) — optional geometry check before HPC submission
