---
name: "tikz-track-e"
description: "Deterministic helpers for Track E .tex edits in tikz_writer: swap_node_coords, simplify_adjacent_edges, reroute_back_edge, inline_legend. 替代手写正则, 避免 .tex 误改, Track E 坐标编辑, back-edge 重路由, legend 内联, 同行邻接边简化."
revision: 1
---

# tikz-track-e — Track E deterministic operations

> Crystallized from: 4 rounds of Track E manual edits on tikz_writer integration
> tests (13-node DAG + back-edge). Each operation below was previously executed
> by hand on the `.tex` and is now reproducible via `track_e_ops.py`.

## When to Use

Invoke this skill from **Diagram Architect Track E** when the post-MCP `.tex`
needs one of the four common, deterministic transformations:

- **`swap_node_coords`** — swap `at (x, y)` coordinates between two nodes
  (e.g. fix x-order to match topological order on a single layer).
- **`simplify_adjacent_edges`** — turn `\draw[...] (A) -- (waypoint) -- (B)`
  for adjacent same-row nodes into `(A) -- (B)` (kills detour artifacts left
  by orthogonal routing).
- **`reroute_back_edge`** — replace one back-edge `\draw` with a single
  `to[out=...,in=...,looseness=...]` segment plus optional bend hint
  (`bend left=N`).
- **`inline_legend`** — fold a separate `\matrix`/`\node[legend]` block into a
  TikZ scope right of the diagram, preserving entries.

## When NOT to Use

- Topology is wrong (missing nodes / wrong connections) → fix DSL via Track A
  first; do not patch `.tex`.
- Fundamental layout rewrite → use `track-e-tex-editing` skill (full coordinate
  rewrite). This skill only does **local, deterministic** patches.
- Non-tikz_writer-generated `.tex` (handwritten or other tools) → operations
  may `status=failed`; caller must fall back to manual edit.

## How to Invoke (Workflow)

## Workflow

1. **Read .tex**: locate the latest tikz_writer-generated `.tex` (typically
   under `output/build/`).
2. **Pick op**: select one of the 4 deterministic ops based on the symptom:
   - x-order on a row wrong → `swap_node_coords`
   - same-row adjacent edge with detour waypoint → `simplify_adjacent_edges`
   - back-edge drawn through layer → `reroute_back_edge`
   - separate legend block disrupting layout → `inline_legend`
3. **Invoke**: call the helper (Python API or CLI). Each op edits the file in
   place and returns `{status, modified_lines, warnings}`.
4. **Validate**: re-compile via `xelatex` (mind `TEXINPUTS`, see Pitfalls);
   then run `extract_shadow_dsl.py` + `aabb_check.py` (A2/A3) to confirm no
   topology loss and no new collisions.
5. **Iterate**: if `status == "failed"` or validation regresses, revert the
   `.tex` from VCS and fall back to manual edit.

## API Reference

```python
from track_e_ops import (
    swap_coords,
    simplify_edges,
    reroute_back_edge,
    inline_legend,
)

# 1. Swap two nodes' coordinates
result = swap_coords("output/build/workflow.tex", swaps=[("nodeA", "nodeB")])
# result == {"status": "ok", "modified_lines": 2, "warnings": []}

# 2. Simplify adjacent-row edges
result = simplify_edges("output/build/workflow.tex",
                        edges=[("A", "B"), ("C", "D")])

# 3. Reroute one back-edge with bend hint
result = reroute_back_edge("output/build/workflow.tex",
                           edge=("end", "start"),
                           waypoints={"out": 90, "in": 90, "looseness": 1.6})

# 4. Inline a legend block
result = inline_legend("output/build/workflow.tex")
```

All four return:
```python
{"status": "ok" | "failed", "modified_lines": int, "warnings": [str, ...]}
```

`status == "failed"` means the regex did not match anything; caller should
treat as no-op and fall back to manual edit.

## CLI

```bash
python3 scripts/track_e_ops.py --help
```

The CLI mirrors the API for one-shot calls from agent shell tools.

## Common Pitfalls (from 4-round iteration)

1. **`\input{styles/base_style.tex}` resolution**: `xelatex` must run with
   `TEXINPUTS` covering the source dir's `styles/` subdir, OR the file must be
   compiled by tikz_writer's `_export_high_resolution` which now mirrors
   `\input{...}` refs into a temp dir (S5/T3.1).
2. **`back-edge` waypoint hints in `to[...]` are silently ignored on `--`
   paths** — `reroute_back_edge` rewrites the whole `\draw` to use a single
   `to` segment.
3. **`pos=X` label placement on `to`** must be `(A) to node[pos=X] {label} (B)`
   — placing `node[pos=X]` **after** `(B)` anchors the label at B. The helper
   keeps existing label positions intact (it does not move labels).
4. **Adjacent-row edge simplification false positive**: if the waypoint is
   actually meant to dodge a third node, simplification will create a
   collision. Caller must run `aabb_check.py` (A3) after applying.
5. **Coordinate parsing is line-based**. Multi-line `\node[text width=...] (id)
   at (x, y) {long text};` is supported only when `at (x, y)` lives on a
   single line; otherwise `status=failed`.

## Trigger Justification

- **T1** (≥5 distinct deterministic tool-call steps): the 4 operations + their
  shared `.tex` parse routine ⇒ qualifies.
- **T2** (≥3 occurrences across iterations): the same 4 patterns appeared in
  every Track E round of the integration test.

## See Also

- `track-e-tex-editing/SKILL.md` — full-coordinate Track E workflow (parent).
- `skill-crystallization.instructions.md` — trigger contract.

## Revision Log

- **rev 1** (2026-05-25): Initial crystallization. Four deterministic ops
  (swap_node_coords, simplify_adjacent_edges, reroute_back_edge,
  inline_legend) extracted from 4 rounds of manual Track E edits on the
  tikz_writer integration test (13-node DAG + back-edge). Shipped with
  `extract_shadow_dsl.py` (A2) and `aabb_check.py` (A3) sibling helpers.
