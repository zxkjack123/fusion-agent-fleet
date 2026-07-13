"""Unit tests for aabb_check."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from aabb_check import check_collisions  # noqa: E402


def _write(tmp_path, body):
    p = tmp_path / "t.tex"
    p.write_text(body, encoding="utf-8")
    return p


def test_no_collisions_well_spaced(tmp_path):
    body = r"""\begin{tikzpicture}
  \node[box] (a) at (0.0, 0.0) {A};
  \node[box] (b) at (5.0, 0.0) {B};
  \node[box] (c) at (10.0, 0.0) {C};
  \draw[->] (a) -- (b);
  \draw[->] (b) -- (c);
\end{tikzpicture}
"""
    p = _write(tmp_path, body)
    r = check_collisions(p)
    assert r["node_collisions"] == []
    assert r["edge_through_node"] == []


def test_detects_edge_through_node(tmp_path):
    # a, b, c colinear; edge (a -> c) passes through b.
    body = r"""\begin{tikzpicture}
  \node[box] (a) at (0.0, 0.0) {A};
  \node[box] (b) at (5.0, 0.0) {B};
  \node[box] (c) at (10.0, 0.0) {C};
  \draw[->] (a) -- (c);
\end{tikzpicture}
"""
    p = _write(tmp_path, body)
    r = check_collisions(p)
    hits = [t for t in r["edge_through_node"] if t == ("a", "c", "b")]
    assert hits, r["edge_through_node"]


def test_detects_node_overlap(tmp_path):
    body = r"""\begin{tikzpicture}
  \node[box] (a) at (0.0, 0.0) {A};
  \node[box] (b) at (0.2, 0.1) {B};
\end{tikzpicture}
"""
    p = _write(tmp_path, body)
    r = check_collisions(p)
    assert ("a", "b") in r["node_collisions"]
