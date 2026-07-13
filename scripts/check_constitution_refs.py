#!/usr/bin/env python3
"""check_constitution_refs.py — Validate per-agent See-Also references.

Rules:
  1. Parse CONSTITUTION.md, extract top-level "## N. <title>" anchors.
  2. For each .opencode/agent/*.md whose `options.delivery_tier` is one of
     {producer-external, producer-internal, orchestrator}:
       - WARN if no "## See Also" section.
       - FAIL if "## See Also" cites a CONSTITUTION §N that does not
         exist.
  3. Other tiers (specialist, sub-only, utility, gateway, domain) are
     not required to have See Also; skipped silently.

Exit code:
  0 — all FAIL checks passed (WARN allowed).
  1 — at least one FAIL.

Usage:
  python3 scripts/check_constitution_refs.py [--strict]

  --strict   Treat WARN as FAIL (used for B-wave full enforcement).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parent.parent
CONST = REPO / "CONSTITUTION.md"
REQUIRED_TIERS = {"producer-external", "producer-internal", "orchestrator"}

SECTION_RE = re.compile(r"^## (\d+)\. ", re.MULTILINE)
SEE_ALSO_RE = re.compile(r"^## See Also\s*$", re.MULTILINE)
REF_RE = re.compile(r"CONSTITUTION\.md\s*§\s*(\d+)")


def parse_constitution_sections(text: str) -> set[int]:
    return {int(m.group(1)) for m in SECTION_RE.finditer(text)}


def agent_tier(path: Path) -> str | None:
    """Read delivery_tier from sidecar (preferred) or frontmatter."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    parsed = yaml.safe_load(text[4:end]) or {}
    tier = (parsed.get("options") or {}).get("delivery_tier")
    if tier:
        return tier
    # Fallback to sidecar
    sidecar_path = path.with_suffix(".meta.yaml")
    if sidecar_path.is_file():
        sidecar = yaml.safe_load(sidecar_path.read_text(encoding="utf-8")) or {}
        return sidecar.get("delivery_tier")
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if not CONST.exists():
        print(f"FAIL: {CONST} not found", file=sys.stderr)
        return 1

    sections = parse_constitution_sections(CONST.read_text(encoding="utf-8"))
    if not sections:
        print("FAIL: CONSTITUTION.md has no '## N. ' section headings",
              file=sys.stderr)
        return 1

    fails = 0
    warns = 0
    checked = 0

    for agent in sorted((REPO / ".opencode" / "agent").glob("*.md")):
        text = agent.read_text(encoding="utf-8")
        tier = agent_tier(agent)
        if tier not in REQUIRED_TIERS:
            continue
        checked += 1

        if not SEE_ALSO_RE.search(text):
            msg = f"WARN: {agent.name} (tier={tier}) missing '## See Also'"
            print(msg)
            warns += 1
            if args.strict:
                fails += 1
            continue

        # Validate cited §N exists in CONSTITUTION
        body = text.split("## See Also", 1)[1]
        cited = {int(m.group(1)) for m in REF_RE.finditer(body)}
        if not cited:
            print(f"WARN: {agent.name} has 'See Also' but no "
                  f"'CONSTITUTION.md §N' citations")
            warns += 1
            if args.strict:
                fails += 1
            continue

        invalid = cited - sections
        if invalid:
            print(f"FAIL: {agent.name} cites non-existent CONSTITUTION "
                  f"sections: {sorted(invalid)}")
            fails += 1

    print(f"\nSummary: checked={checked}, fails={fails}, warns={warns}, "
          f"strict={args.strict}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
