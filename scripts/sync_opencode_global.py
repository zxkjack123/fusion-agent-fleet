#!/usr/bin/env python3
"""Mirror project OpenCode agents/config context into the user global registry."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_AGENT_DIR = REPO_ROOT / ".opencode" / "agent"
PROJECT_CONTEXT_DIR = REPO_ROOT / ".opencode" / "context"
GLOBAL_ROOT = Path.home() / ".config" / "opencode"
GLOBAL_AGENT_DIR = GLOBAL_ROOT / "agent"
GLOBAL_CONTEXT_DIR = GLOBAL_ROOT / "context"


def mirror_dir(source: Path, target: Path, pattern: str) -> int:
    if not source.is_dir():
        raise SystemExit(f"source directory not found: {source}")
    target.mkdir(parents=True, exist_ok=True)
    for old in target.glob(pattern):
        old.unlink()
    count = 0
    for item in sorted(source.glob(pattern)):
        shutil.copy2(item, target / item.name)
        count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report planned sync without writing global files.",
    )
    args = parser.parse_args()

    agent_count = len(list(PROJECT_AGENT_DIR.glob("*.md")))
    meta_count = len(list(PROJECT_AGENT_DIR.glob("*.meta.yaml")))
    context_count = len(list(PROJECT_CONTEXT_DIR.glob("*.md")))
    if args.dry_run:
        print(f"DRY-RUN: would mirror {agent_count} agent(s) to {GLOBAL_AGENT_DIR}")
        print(f"DRY-RUN: would mirror {meta_count} sidecar file(s) to {GLOBAL_AGENT_DIR}")
        print(f"DRY-RUN: would mirror {context_count} context file(s) to {GLOBAL_CONTEXT_DIR}")
        return 0

    mirrored_agents = mirror_dir(PROJECT_AGENT_DIR, GLOBAL_AGENT_DIR, "*.md")
    mirrored_meta = mirror_dir(PROJECT_AGENT_DIR, GLOBAL_AGENT_DIR, "*.meta.yaml")
    mirrored_context = mirror_dir(PROJECT_CONTEXT_DIR, GLOBAL_CONTEXT_DIR, "*.md")
    print(f"Mirrored {mirrored_agents} opencode agent(s) to {GLOBAL_AGENT_DIR}")
    print(f"Mirrored {mirrored_meta} sidecar file(s) to {GLOBAL_AGENT_DIR}")
    print(f"Mirrored {mirrored_context} opencode context file(s) to {GLOBAL_CONTEXT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
