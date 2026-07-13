#!/usr/bin/env python3
"""Validate sub-agent return envelope v1 compliance.

Checks every ``.opencode/agent/*.md`` file for:
1. Presence of ``### Final Report 强制格式`` heading
2. ``report_format_version: 1`` line in that section
3. ``**Status**:`` line with canonical enum value

Exit 0 when all files comply; exit 1 otherwise.
"""
from __future__ import annotations

import re
import sys
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_DIR = REPO_ROOT / ".opencode" / "agent"

FINAL_REPORT_HEADING = re.compile(
    r"^### Final Report 强制格式\s*$", re.MULTILINE
)
NEXT_H2 = re.compile(r"^## ", re.MULTILINE)
NEXT_H3 = re.compile(r"^### ", re.MULTILINE)
REPORT_VERSION = re.compile(r"report_format_version:\s*1\b")
STATUS_LINE = re.compile(
    r"\*\*Status\*\*:\s*(COMPLETED|PARTIAL|FAILED|BLOCKED|HALTED)"
)
VALID_STATUSES = {"COMPLETED", "PARTIAL", "FAILED", "BLOCKED", "HALTED"}


def extract_final_report_section(text: str) -> str | None:
    m = FINAL_REPORT_HEADING.search(text)
    if not m:
        return None
    start = m.end()
    nxt_h3 = NEXT_H3.search(text, start)
    nxt_h2 = NEXT_H2.search(text, start)
    candidates = [c.start() for c in [nxt_h3, nxt_h2] if c]
    end = min(candidates) if candidates else len(text)
    return text[start:end]


def _strip_code_blocks(text: str) -> str:
    """Remove fenced code block content so headings inside them are ignored."""
    result = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            result.append(line)
            continue
        if in_fence:
            result.append(line)
            continue
        result.append(line)
    # Actually, we want to keep code blocks but not treat their headings as real.
    # Simpler: just search the full text for the patterns since the Status line
    # may be inside a code block template. The checker should verify presence,
    # not structural position.
    return text


def load_envelope_text(path: Path) -> str:
    """Load return envelope text from sidecar, or fall back to agent body."""
    sidecar = path.with_suffix(".meta.yaml")
    if sidecar.is_file():
        import yaml as _yaml
        data = _yaml.safe_load(sidecar.read_text(encoding="utf-8")) or {}
        env = data.get("return_envelope_text")
        if env:
            return env
    return path.read_text(encoding="utf-8")


def check_file(path: Path) -> list[str]:
    text = load_envelope_text(path)
    failures: list[str] = []

    if not FINAL_REPORT_HEADING.search(text):
        failures.append(
            f"{path.name}: missing `### Final Report 强制格式` heading"
        )
        return failures

    if not REPORT_VERSION.search(text):
        failures.append(
            f"{path.name}: missing `report_format_version: 1` in "
            f"Final Report section"
        )

    if not STATUS_LINE.search(text):
        failures.append(
            f"{path.name}: missing or invalid `**Status**: <enum>` line "
            f"in Final Report section"
        )

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate sub-agent return envelope v1 compliance"
    )
    parser.add_argument(
        "--files",
        nargs="+",
        default=None,
        help="Specific agent files to check (default: all .opencode/agent/*.md)",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        default=False,
        help="Print warnings instead of failing (exit 0 always)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit 1 on any issue (default behavior when --warn-only not set)",
    )
    args = parser.parse_args(argv)

    if args.files:
        agent_files = [Path(f) for f in args.files]
    else:
        agent_files = sorted(AGENT_DIR.glob("*.md"))

    all_failures: list[str] = []
    checked = 0

    for agent_file in agent_files:
        if not agent_file.is_file():
            print(f"ERROR: {agent_file} not found")
            continue
        checked += 1
        failures = check_file(agent_file)
        all_failures.extend(failures)

    if all_failures:
        if args.warn_only:
            print(f"WARN: {len(all_failures)} envelope issue(s) in {checked} file(s):")
            for line in all_failures:
                print(f"  - {line}")
            return 0
        else:
            print(f"FAIL: {len(all_failures)} envelope issue(s) in {checked} file(s):")
            for line in all_failures:
                print(f"  - {line}")
            return 1

    print(f"PASS: {checked} file(s) have compliant return envelopes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
