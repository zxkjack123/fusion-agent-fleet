---
name: "mcnp-native-plot-only"
description: "Use when: creating native MCNP6 geometry plots from large MCNP decks by extracting plot-only local universe inputs, serial plot-enabled MCNP6, PostScript-to-PNG conversion, section selection, U= universe plotting. MCNP原生plot, 几何检查, 局部universe, plot-only输入, 偏滤器/屏蔽几何截图."
revision: 1
---

# MCNP Native Plot-Only Geometry Workflow

> Crystallized from: BEST divertor bottom shielding geometry check, where a full MCNP deck was too slow to plot directly and the relevant region was inside `U=31`.
> Date: 2026-05-16
> Trigger: T1 + T3

## When to Use

- A large MCNP input deck contains source, mesh tally, weight-window, or other non-geometry data cards that make native `mcnp6 ip ... plotm=...` slow or fragile.
- The user needs **native MCNP6 geometry plot** images, not an approximate external CSG sampler.
- The geometry of interest is inside a local universe such as `U=31`, and a global `px/py/pz` slice misses or obscures the relevant cells.
- You need to choose and document screenshot parameters: `origin`, `basis`, `extent`, `level`, labels, color mode, and conversion to PNG.
- You need to compare geometry/material changes across several related decks, such as `worst`, `void`, and material-filled variants.

## When NOT to Use

- The task is a production transport calculation, tally extraction, or HPC job submission. Use the relevant MCNP/HPC run workflow instead.
- The full input plots quickly and correctly with native MCNP; in that case, do not generate plot-only inputs unless a local universe needs isolation.
- The requested output is a physics result, dose map, or flux/heating post-processing figure rather than a geometry plot.
- The geometry uses complex lattice/fill behavior that must be inspected in its exact parent context; plot-only local-universe extraction may hide parent-level clipping and should be treated as a focused diagnostic only.

## Workflow

### 1. Confirm the MCNP executable really supports plot

1. Do not assume MPI and serial binaries have the same compile features.
2. Probe candidate executables with the version/config output and look for `plot` or `PLOT` in the configuration.
3. Prefer a serial plot-enabled executable for local geometry screenshots.

Example validated path from the source task:

- `/home/gw/opt/MCNP6/Source/src.backup-20260206-113848/mcnp6`
- Expected capability marker: `CONFIG = plot gfortran omp`, `MPI = no`

If only MPI binaries are available and they lack plot support, report that limitation; do not claim MCNP cannot plot globally unless all relevant binaries were checked.

### 2. Identify the actual geometry level and target cells

1. Locate the cells or materials that must be checked.
2. Inspect whether those cells are in a local universe with `U=<id>`.
3. Extract their surface references and nearby cells, then inspect the corresponding surface definitions.
4. Search for `TR<id>` / `*TR<id>` used by those surfaces or fills.

Important interpretation rule:

- A transform such as `tr31 0.01 0.01 0.01` is only a small translation, not a rotation.
- If a simple global `x-z` slice fails, the cause may be wrong universe/region focus rather than a missing coordinate rotation.

### 3. Choose section planes from geometry, not habit

Choose `origin`, `basis`, and `extent` from the target surfaces and physical question.

Useful plot commands:

```text
term 0
viewport rect
color by mat
label 0 0.45 cel
origin <x> <y> <z>
basis <sx> <sy> <sz> <tx> <ty> <tz>
extent <s> <t>
file all

end
```

Recommended plane types:

| Plane | How to choose | Purpose |
|---|---|---|
| Local radial-vertical | `basis 1 0 0 0 0 1` or transformed local equivalent | Main geometry/material check |
| Horizontal bottom slice | `basis 1 0 0 0 1 0` at key `z` | Check bottom shielding fill/void pattern |
| Sector-angle vertical slice | `basis cos(phi) sin(phi) 0 0 0 1` | Check wedge/sector boundaries at a specific toroidal angle |
| Oblique feature slice | Align first basis vector with an important plane/surface normal or tangent | Check slanted shield boundaries |

For wedge-like sectors, inspect plane normals such as `P a b c d` and derive approximate angles from `atan2(y, x)` or from the mid-angle of bounding surfaces.

### 4. Create plot-only input safely

Do **not** edit the production MCNP deck. Generate a temporary input under a plot output directory.

For local universe plotting:

1. Split the deck into title, cell block, surface block, and data block.
2. Keep active cells with `U=<target_universe>`.
3. Remove the `U=<target_universe>` attribute from those kept cells so the local universe becomes level-0 geometry.
4. Keep the surface definitions referenced by the local universe. If dependency tracing is hard, retaining the full surface block is acceptable for plotting, but expect many “surface is not used” warnings.
5. Keep only geometry transforms (`TRn`, `*TRn`) from the data block.
6. Add `mode n` and minimal dummy material cards for all positive material numbers used by the kept cells. The isotope choice is irrelevant for geometry plotting because no transport is run.
7. Omit source, tally, FMESH, WWP, WWG, NPS production cards, and other non-geometry data cards.

Typical dummy material pattern:

```text
mode n
tr31 0.01 0.01 0.01
c Dummy material cards suppress missing-M fatal errors during plotting.
m62 1001 1
m217 1001 1
nps 0
```

### 5. Run native MCNP plot and convert output

Run serial MCNP in plot mode:

```text
mcnp6 ip i=<plot_only_input> com=<plot_command_file> plotm=<output_stem>
```

Expected output:

- `<output_stem>.ps` — native MCNP PostScript plot
- `outp`, `comout`, run log

Convert PostScript to PNG with Ghostscript:

```text
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pngalpha -r150 -sOutputFile=<output>.png <output>.ps
```

For chat preview, keep the longest side ≤2000 px. Preserve full-resolution deliverables separately.

### 6. Compare and document

For each view, compare all relevant decks with the same `origin`, `basis`, and `extent`.

Document:

- MCNP executable path and plot capability marker.
- Whether the input was full-deck or plot-only.
- The target universe and target cells.
- Exact plot commands for each view.
- Output paths for `.ps`, `.png`, and readable/cropped images.
- Limitations: local-universe plot checks internal geometry; parent-level clipping/fill context still needs separate review if relevant.

## Inputs & Outputs

| Input | Source |
|---|---|
| MCNP production decks | User workspace / simulation directory |
| Target cells/materials/universe | User request or extracted from MCNP cell cards |
| Plot-enabled serial MCNP6 executable | Local MCNP installation |
| Candidate section planes | Derived from target surfaces and physical geometry |

| Output | Format |
|---|---|
| Plot-only MCNP inputs | Temporary `.i` files under a plot directory |
| MCNP plot command files | `.com` files with `origin`, `basis`, `extent`, `file all`, `end` |
| Native plot files | `.ps` from MCNP6 |
| Preview/deliverable images | `.png` from Ghostscript/ImageMagick |
| Report text | Markdown section with plot parameters and caveats |

## Common Pitfalls

- **Assuming “MCNP cannot plot” from the MPI binary only**: serial builds may include `PLOT` even when MPI builds do not.
- **Using global `x-z` by habit**: the relevant geometry may be in a local universe or toroidal wedge; derive the plane from target surfaces.
- **Leaving WWP cards in a plot run**: MCNP may still require missing `wwinp`. Remove WWP/WWG cards from plot-only input.
- **Using the full deck for plotting**: large source/FMESH data can keep MCNP in input listing/checking for many minutes before any image is written.
- **Forgetting dummy material cards**: MCNP can still emit `fatal error. no m card for material no. ...` before completing plot setup.
- **Misreading `TR` cards**: `tr31 0.01 0.01 0.01` is a translation only; do not invent a rotation.
- **Overclaiming local-universe plots**: extracting `U=<id>` is excellent for internal geometry/material checks, but it does not prove parent-level clipping/fill context unless separately plotted.
- **Oversized previews**: make a ≤2000 px preview copy before displaying many images; keep high-resolution outputs for delivery.

## Revision Log

| Rev | Date | Change | Source |
|---|---|---|---|
| 1 | 2026-05-16 | Initial crystallization of MCNP local-universe plot-only native plotting workflow | BEST divertor bottom shielding serial MCNP plot task |
