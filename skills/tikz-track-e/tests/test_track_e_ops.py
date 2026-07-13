"""Unit tests for track_e_ops."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from track_e_ops import (  # noqa: E402
    inline_legend,
    reroute_back_edge,
    simplify_edges,
    swap_coords,
)

_TEX_SAMPLE = r"""\begin{tikzpicture}
  \node[box] (a) at (0.0, 0.0) {A};
  \node[box] (b) at (2.0, 0.0) {B};
  \node[box] (c) at (4.0, 0.0) {C};
  \node[box] (d) at (0.0, 2.0) {D};
  \draw[->] (a) -- (b);
  \draw[->] (b) -- (vw1) -- (c);
  \draw[->] (d) -- (mid) -- (a);
  \matrix[legend, draw] (leg) at (8, 0) {
    \node {Key}; \\
  };
\end{tikzpicture}
"""


def _fresh_tex(tmp_path):
    p = tmp_path / "t.tex"
    p.write_text(_TEX_SAMPLE, encoding="utf-8")
    return p


def test_swap_coords(tmp_path):
    p = _fresh_tex(tmp_path)
    r = swap_coords(p, [("a", "c")])
    assert r["status"] == "ok"
    assert r["modified_lines"] == 2
    text = p.read_text(encoding="utf-8")
    assert "(a) at (4, 0)" in text
    assert "(c) at (0, 0)" in text


def test_simplify_edges(tmp_path):
    p = _fresh_tex(tmp_path)
    r = simplify_edges(p, [("b", "c")])
    assert r["status"] == "ok"
    assert r["modified_lines"] >= 1
    text = p.read_text(encoding="utf-8")
    assert "(b) -- (c)" in text
    assert "(vw1)" not in text


def test_reroute_back_edge(tmp_path):
    p = _fresh_tex(tmp_path)
    r = reroute_back_edge(p, ("d", "a"),
                          {"out": 180, "in": 180, "looseness": 1.8})
    assert r["status"] == "ok"
    assert r["modified_lines"] == 1
    text = p.read_text(encoding="utf-8")
    assert "to[out=180,in=180,looseness=1.8]" in text
    assert "(mid)" not in text or "-- (mid) --" not in text


def test_inline_legend(tmp_path):
    p = _fresh_tex(tmp_path)
    r = inline_legend(p)
    assert r["status"] == "ok"
    assert "% TRACK_E_INLINE_LEGEND" in p.read_text(encoding="utf-8")


def test_swap_missing_node_returns_failed(tmp_path):
    p = _fresh_tex(tmp_path)
    r = swap_coords(p, [("a", "zzz")])
    assert r["status"] == "failed"
    assert any("zzz" in w for w in r["warnings"])
