#!/usr/bin/env python3
"""Shadow DSL extractor for Track E.

Given a tikz_writer-generated `.tex` file, parse `\\node ... at (x, y) {label}`
and `\\draw ... (src) ... (tgt)` lines and return a structured dict suitable
for structural cross-checks against the source DSL.

Returns:
    {
        "nodes": [{"id": str, "x": float, "y": float, "label": str}, ...],
        "edges": [{"src": str, "tgt": str, "waypoints": [str, ...]}, ...]
    }

CLI:
    python3 extract_shadow_dsl.py <tex_path>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


_NODE_RE = re.compile(
    r"\\node\b[^()]*?\(([A-Za-z0-9_\-]+)\)\s*at\s*\("
    r"(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\)\s*\{(.*?)\}\s*;",
    re.DOTALL,
)

_DRAW_RE = re.compile(
    r"\\draw\b[^;]*?;",
    re.DOTALL,
)

_PAREN_ID_RE = re.compile(r"\(([A-Za-z0-9_\-]+)\)")


def extract_shadow_dsl(tex_path: str | Path) -> dict:
    """Parse `.tex` into shadow DSL structure (see module docstring)."""
    text = Path(tex_path).read_text(encoding="utf-8")
    nodes: list[dict] = []
    node_ids: set[str] = set()
    for m in _NODE_RE.finditer(text):
        nid = m.group(1)
        if nid in node_ids:
            continue
        node_ids.add(nid)
        label = m.group(4).strip()
        # Strip trailing TikZ formatting like ``\\`` or ``\strut``.
        label = re.sub(r"\\\\\s*$", "", label).strip()
        nodes.append(
            {
                "id": nid,
                "x": float(m.group(2)),
                "y": float(m.group(3)),
                "label": label,
            }
        )

    edges: list[dict] = []
    for m in _DRAW_RE.finditer(text):
        body = m.group(0)
        ids = [pid for pid in _PAREN_ID_RE.findall(body) if pid in node_ids]
        if len(ids) < 2:
            continue
        src, tgt = ids[0], ids[-1]
        waypoints = ids[1:-1]
        edges.append({"src": src, "tgt": tgt, "waypoints": waypoints})

    return {"nodes": nodes, "edges": edges}


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="extract_shadow_dsl")
    parser.add_argument("tex_path")
    args = parser.parse_args(argv)
    result = extract_shadow_dsl(args.tex_path)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
