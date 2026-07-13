#!/usr/bin/env python3
"""Validate that every OpenCode agent declares a canonical delivery_tier."""
from __future__ import annotations

import re
import sys
from pathlib import Path
import yaml

ALLOWED = {
    "producer-external",
    "producer-internal",
    "orchestrator",
    "specialist",
    "sub-only",
    "gateway",
    "domain",
    "utility",
}


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    agents = sorted((repo_root / ".opencode" / "agent").glob("*.md"))
    failures: list[str] = []
    checked = 0
    for path in agents:
        text = path.read_text(encoding="utf-8")
        end = text.find("\n---", 4)
        data = yaml.safe_load(text[4:end]) or {}
        # Read delivery_tier from sidecar (preferred) or frontmatter options
        tier = None
        sidecar_path = path.with_suffix(".meta.yaml")
        if sidecar_path.is_file():
            sidecar = yaml.safe_load(sidecar_path.read_text(encoding="utf-8")) or {}
            tier = sidecar.get("delivery_tier")
        if not tier:
            tier = (data.get("options") or {}).get("delivery_tier")
        if not tier:
            failures.append(f"{path.name}: missing delivery_tier")
            continue
        if tier not in ALLOWED:
            failures.append(f"{path.name}: unknown delivery_tier '{tier}'")
            continue
        checked += 1

    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1
    print(f"PASS: {checked} agents within tier allowlist (8 canonical tiers)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
