"""Unit tests for extract_shadow_dsl."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from extract_shadow_dsl import extract_shadow_dsl  # noqa: E402

_SAMPLE = r"""\begin{tikzpicture}
  \node[box] (a) at (0.0, 0.0) {Alpha};
  \node[box] (b) at (2.0, 0.0) {Beta};
  \node[box] (c) at (4.0, 0.0) {Gamma};
  \draw[->] (a) -- (b);
  \draw[->] (b) -- (mid) -- (c);
  \draw[->] (c) to[out=90,in=90,looseness=1.5] (a);
\end{tikzpicture}
"""


def test_extract_nodes_and_edges(tmp_path):
    p = tmp_path / "t.tex"
    p.write_text(_SAMPLE, encoding="utf-8")
    r = extract_shadow_dsl(p)
    assert len(r["nodes"]) == 3
    ids = {n["id"] for n in r["nodes"]}
    assert ids == {"a", "b", "c"}
    labels = {n["id"]: n["label"] for n in r["nodes"]}
    assert labels["a"] == "Alpha"
    assert len(r["edges"]) == 3
    edge_pairs = {(e["src"], e["tgt"]) for e in r["edges"]}
    assert ("a", "b") in edge_pairs
    assert ("b", "c") in edge_pairs
    assert ("c", "a") in edge_pairs
    # Waypoint preserved on the middle edge
    middle = [e for e in r["edges"] if e["src"] == "b" and e["tgt"] == "c"][0]
    # (mid) is not declared as a node, so it should NOT appear as waypoint
    assert middle["waypoints"] == []


def test_extract_handles_empty_tex(tmp_path):
    p = tmp_path / "empty.tex"
    p.write_text("% empty\n", encoding="utf-8")
    r = extract_shadow_dsl(p)
    assert r == {"nodes": [], "edges": []}
