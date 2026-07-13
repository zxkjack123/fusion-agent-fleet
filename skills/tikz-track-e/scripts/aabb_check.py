#!/usr/bin/env python3
"""Post-compile AABB collision check for Track E.

Loads shadow DSL via `extract_shadow_dsl` and runs two AABB tests:

1. **Node–node overlap**: every pair of node bboxes intersected.
2. **Edge through non-endpoint node**: every edge segment intersected
   against every non-endpoint node bbox.

Returns:
    {"node_collisions": [(a, b), ...],
     "edge_through_node": [(src, tgt, node_id), ...]}

CLI:
    python3 aabb_check.py <tex_path> [--node-w W] [--node-h H]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_shadow_dsl import extract_shadow_dsl  # noqa: E402


def _bbox(node, w: float, h: float) -> tuple[float, float, float, float]:
    x, y = node["x"], node["y"]
    return (x - w / 2, y - h / 2, x + w / 2, y + h / 2)


def _aabb_overlap(b1, b2) -> bool:
    return not (b1[2] < b2[0] or b2[2] < b1[0] or b1[3] < b2[1] or b2[3] < b1[1])


def _seg_intersects_rect(p1, p2, rect) -> bool:
    """Liang–Barsky segment vs AABB intersection."""
    x1, y1 = p1
    x2, y2 = p2
    xmin, ymin, xmax, ymax = rect
    dx, dy = x2 - x1, y2 - y1
    p = [-dx, dx, -dy, dy]
    q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]
    u1, u2 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return False
        else:
            t = qi / pi
            if pi < 0:
                if t > u2:
                    return False
                if t > u1:
                    u1 = t
            else:
                if t < u1:
                    return False
                if t < u2:
                    u2 = t
    return u1 <= u2


def check_collisions(
    tex_path: str | Path,
    node_size_default: tuple[float, float] = (1.8, 0.6),
) -> dict:
    """Run AABB checks against the shadow DSL extracted from ``tex_path``."""
    nw, nh = node_size_default
    shadow = extract_shadow_dsl(tex_path)
    nodes = {n["id"]: n for n in shadow["nodes"]}
    bboxes = {nid: _bbox(n, nw, nh) for nid, n in nodes.items()}

    node_collisions: list[tuple[str, str]] = []
    ids = sorted(nodes.keys())
    for i, a in enumerate(ids):
        for b in ids[i + 1 :]:
            if _aabb_overlap(bboxes[a], bboxes[b]):
                node_collisions.append((a, b))

    edge_through: list[tuple[str, str, str]] = []
    for e in shadow["edges"]:
        src, tgt = e["src"], e["tgt"]
        if src not in nodes or tgt not in nodes:
            continue
        p1 = (nodes[src]["x"], nodes[src]["y"])
        p2 = (nodes[tgt]["x"], nodes[tgt]["y"])
        for nid, n in nodes.items():
            if nid in (src, tgt):
                continue
            if _seg_intersects_rect(p1, p2, bboxes[nid]):
                edge_through.append((src, tgt, nid))

    return {
        "node_collisions": node_collisions,
        "edge_through_node": edge_through,
    }


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aabb_check")
    parser.add_argument("tex_path")
    parser.add_argument("--node-w", type=float, default=1.8)
    parser.add_argument("--node-h", type=float, default=0.6)
    args = parser.parse_args(argv)
    result = check_collisions(args.tex_path, (args.node_w, args.node_h))
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if not result["edge_through_node"] else 1


if __name__ == "__main__":
    raise SystemExit(_main())
