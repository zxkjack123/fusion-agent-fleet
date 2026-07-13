#!/usr/bin/env python3
"""Inspect OpenCode per-agent permission surfaces.

This replaces the old VSCode 128-tool-cap budget check. OpenCode no longer
needs VSCode virtual-tool workarounds, but we still keep a lightweight gate for
forbidden permissions and unexpectedly broad agent permission surfaces.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_DIR = REPO_ROOT / ".opencode" / "agent"
WARN_THRESHOLD = 80
FAIL_THRESHOLD = 120
FORBIDDEN_PERMISSION_KEYS = {
    "thunderbird-mcp-server_tb_send_message": (
        "Thunderbird send must remain outside agent authority; use draft + manual review"
    ),
}


def read_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    parsed = yaml.safe_load(text[4:end]) or {}
    return parsed if isinstance(parsed, dict) else {}


def permission_weight(permission: dict | str | None) -> tuple[int, list[str]]:
    if permission is None:
        return 0, []
    if isinstance(permission, str):
        return 1, []
    if not isinstance(permission, dict):
        return 0, []
    total = 0
    forbidden = []
    for key, value in permission.items():
        if key in FORBIDDEN_PERMISSION_KEYS and value != "deny":
            forbidden.append(key)
        if isinstance(value, dict):
            total += len(value)
        else:
            total += 1
    return total, forbidden


def status_for_total(total: int) -> str:
    if total > FAIL_THRESHOLD:
        return "FAIL"
    if total > WARN_THRESHOLD:
        return "WARN"
    return "OK"


def main() -> int:
    agent_files = sorted(AGENT_DIR.glob("*.md"))
    if not agent_files:
        print(f"ERROR: no OpenCode agents found under {AGENT_DIR}", file=sys.stderr)
        return 2

    rows: list[tuple[str, int, str]] = []
    worst_exit = 0
    for agent_path in agent_files:
        frontmatter = read_frontmatter(agent_path)
        total, forbidden = permission_weight(frontmatter.get("permission"))
        status = status_for_total(total)
        if status == "WARN" and worst_exit < 1:
            worst_exit = 1
        if status == "FAIL":
            worst_exit = 2
        for key in forbidden:
            print(
                f"ERROR: agent {agent_path.name} grants forbidden permission '{key}': "
                f"{FORBIDDEN_PERMISSION_KEYS[key]}",
                file=sys.stderr,
            )
            status = "FAIL"
            worst_exit = 2
        rows.append((agent_path.stem, total, status))

    print("agent\tpermission_rules\tstatus")
    for row in sorted(rows, key=lambda item: (-item[1], item[0])):
        print("\t".join(str(value) for value in row))
    print(
        f"\n# OpenCode permission thresholds: WARN > {WARN_THRESHOLD}, FAIL > {FAIL_THRESHOLD}",
        file=sys.stderr,
    )
    return worst_exit


if __name__ == "__main__":
    raise SystemExit(main())
