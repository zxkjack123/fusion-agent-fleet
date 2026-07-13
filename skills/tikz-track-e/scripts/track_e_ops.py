#!/usr/bin/env python3
"""Track E deterministic .tex operations.

Provides four idempotent helpers for editing tikz_writer-generated `.tex`
files in Track E. Each helper parses the file line-by-line, applies a single
local transformation, and writes the file back in place.

Operations:
    swap_coords(tex_path, swaps)
    simplify_edges(tex_path, edges)
    reroute_back_edge(tex_path, edge, waypoints)
    inline_legend(tex_path)

All return a dict ``{"status": "ok"|"failed", "modified_lines": int,
"warnings": [str, ...]}``. ``status == "failed"`` means no matching pattern
was found; caller should treat as no-op.

CLI:
    python3 track_e_ops.py --help
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable, Mapping

_NODE_AT_RE = re.compile(
    r"^(?P<lead>\s*\\node\b[^()]*?\()(?P<id>[A-Za-z0-9_\-]+)"
    r"(?P<mid>\)\s*at\s*\()(?P<x>-?\d+(?:\.\d+)?)\s*,\s*"
    r"(?P<y>-?\d+(?:\.\d+)?)(?P<tail>\).*)$"
)

_DRAW_LINE_RE = re.compile(
    r"^(?P<lead>\s*\\draw\b[^;]*?\()(?P<src>[A-Za-z0-9_\-]+)\)"
    r"(?P<mid>.*?\()(?P<tgt>[A-Za-z0-9_\-]+)\)(?P<tail>.*)$"
)


def _parse_nodes(lines: list[str]) -> dict[str, tuple[int, float, float]]:
    """Return {node_id: (line_idx, x, y)} for every \\node ... at (x,y)."""
    out: dict[str, tuple[int, float, float]] = {}
    for i, line in enumerate(lines):
        m = _NODE_AT_RE.match(line)
        if m:
            out[m.group("id")] = (i, float(m.group("x")), float(m.group("y")))
    return out


def swap_coords(
    tex_path: str | Path, swaps: Iterable[tuple[str, str]]
) -> dict:
    """Swap ``at (x,y)`` between each ``(node_a, node_b)`` pair."""
    path = Path(tex_path)
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    nodes = _parse_nodes(lines)
    modified = 0
    warnings: list[str] = []
    for a, b in swaps:
        if a not in nodes or b not in nodes:
            warnings.append(f"node missing: {a if a not in nodes else b}")
            continue
        ia, ax, ay = nodes[a]
        ib, bx, by = nodes[b]
        lines[ia] = _NODE_AT_RE.sub(
            lambda m: f"{m.group('lead')}{m.group('id')}{m.group('mid')}"
            f"{bx:g}, {by:g}{m.group('tail')}",
            lines[ia],
        )
        lines[ib] = _NODE_AT_RE.sub(
            lambda m: f"{m.group('lead')}{m.group('id')}{m.group('mid')}"
            f"{ax:g}, {ay:g}{m.group('tail')}",
            lines[ib],
        )
        modified += 2
    if modified:
        path.write_text("".join(lines), encoding="utf-8")
        return {"status": "ok", "modified_lines": modified, "warnings": warnings}
    return {"status": "failed", "modified_lines": 0, "warnings": warnings or ["no swap applied"]}


def simplify_edges(
    tex_path: str | Path, edges: Iterable[tuple[str, str]]
) -> dict:
    """Rewrite ``\\draw (A) -- (W) -- (B)`` to ``\\draw (A) -- (B)`` per edge."""
    path = Path(tex_path)
    text = path.read_text(encoding="utf-8")
    modified = 0
    warnings: list[str] = []
    for a, b in edges:
        pat = re.compile(
            rf"(\\draw\b[^;]*?\({re.escape(a)}\))"
            rf"(?:\s*--\s*\([A-Za-z0-9_\-]+\))+"
            rf"(\s*--\s*\({re.escape(b)}\))"
        )
        new_text, count = pat.subn(r"\1\2", text)
        if count:
            text = new_text
            modified += count
        else:
            warnings.append(f"no waypoint edge to simplify: ({a})--...--({b})")
    if modified:
        path.write_text(text, encoding="utf-8")
        return {"status": "ok", "modified_lines": modified, "warnings": warnings}
    return {"status": "failed", "modified_lines": 0, "warnings": warnings or ["no edge simplified"]}


def reroute_back_edge(
    tex_path: str | Path,
    edge: tuple[str, str],
    waypoints: Mapping[str, float | int],
) -> dict:
    """Rewrite a back-edge ``\\draw (src) -- ... -- (tgt)`` as a single
    ``to[out=O,in=I,looseness=L]`` segment."""
    path = Path(tex_path)
    text = path.read_text(encoding="utf-8")
    src, tgt = edge
    out_v = waypoints.get("out", 90)
    in_v = waypoints.get("in", 90)
    loose = waypoints.get("looseness", 1.5)
    pat = re.compile(
        rf"(\\draw\b[^;]*?)\({re.escape(src)}\)"
        rf"(?:\s*--\s*\([A-Za-z0-9_\-]+\))*"
        rf"\s*--\s*\({re.escape(tgt)}\)"
    )
    replacement = (
        rf"\g<1>({src}) to[out={out_v},in={in_v},looseness={loose}] ({tgt})"
    )
    new_text, count = pat.subn(replacement, text)
    if count:
        path.write_text(new_text, encoding="utf-8")
        return {"status": "ok", "modified_lines": count, "warnings": []}
    return {
        "status": "failed",
        "modified_lines": 0,
        "warnings": [f"back-edge ({src})->({tgt}) not found"],
    }


_LEGEND_BLOCK_RE = re.compile(
    r"\\begin\{tikzpicture\}\[legend.*?\}\\end\{tikzpicture\}",
    re.DOTALL,
)
_MATRIX_LEGEND_RE = re.compile(
    r"\\matrix\b[^;]*?legend[^;]*?\{.*?\};",
    re.DOTALL,
)


def inline_legend(tex_path: str | Path) -> dict:
    """Mark a separate ``\\matrix[legend ...]`` block for inline embedding.

    The helper does not move text across `\\begin{tikzpicture}` boundaries
    (that requires layout knowledge the agent supplies). Instead it tags the
    block by appending a `% TRACK_E_INLINE_LEGEND` marker so subsequent
    coordinate writes can place it. Returns failed if no legend block is
    found.
    """
    path = Path(tex_path)
    text = path.read_text(encoding="utf-8")
    marker = "% TRACK_E_INLINE_LEGEND"
    if marker in text:
        return {"status": "ok", "modified_lines": 0, "warnings": ["already marked"]}
    for pat in (_MATRIX_LEGEND_RE, _LEGEND_BLOCK_RE):
        m = pat.search(text)
        if m:
            new_text = text[: m.end()] + f"\n{marker}\n" + text[m.end() :]
            path.write_text(new_text, encoding="utf-8")
            return {"status": "ok", "modified_lines": 1, "warnings": []}
    return {"status": "failed", "modified_lines": 0, "warnings": ["no legend block"]}


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="track_e_ops",
        description="Track E deterministic .tex operations",
    )
    sub = parser.add_subparsers(dest="op", required=True)

    p_swap = sub.add_parser("swap", help="swap_coords")
    p_swap.add_argument("tex_path")
    p_swap.add_argument("--pair", action="append", required=True,
                        help="A,B (may repeat)")

    p_simp = sub.add_parser("simplify", help="simplify_edges")
    p_simp.add_argument("tex_path")
    p_simp.add_argument("--edge", action="append", required=True,
                        help="A,B (may repeat)")

    p_back = sub.add_parser("reroute", help="reroute_back_edge")
    p_back.add_argument("tex_path")
    p_back.add_argument("--edge", required=True, help="src,tgt")
    p_back.add_argument("--out", type=int, default=90)
    p_back.add_argument("--in", dest="in_v", type=int, default=90)
    p_back.add_argument("--looseness", type=float, default=1.5)

    p_leg = sub.add_parser("legend", help="inline_legend")
    p_leg.add_argument("tex_path")

    args = parser.parse_args(argv)
    if args.op == "swap":
        result = swap_coords(args.tex_path,
                             [tuple(p.split(",")) for p in args.pair])
    elif args.op == "simplify":
        result = simplify_edges(args.tex_path,
                                [tuple(e.split(",")) for e in args.edge])
    elif args.op == "reroute":
        a, b = args.edge.split(",")
        result = reroute_back_edge(args.tex_path, (a, b),
                                   {"out": args.out, "in": args.in_v,
                                    "looseness": args.looseness})
    elif args.op == "legend":
        result = inline_legend(args.tex_path)
    else:
        parser.error(f"unknown op {args.op}")
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(_main())
