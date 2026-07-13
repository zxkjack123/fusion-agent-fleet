#!/usr/bin/env python3
"""Validate OpenCode project/global agent registries.

OpenCode is the source of truth. This checker validates `.opencode/agent/*.md`
directly and, for `--target global`, also verifies the global registry mirrors
the project registry.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_AGENT_DIR = REPO_ROOT / ".opencode" / "agent"
GLOBAL_AGENT_DIR = Path.home() / ".config" / "opencode" / "agent"
BUILTIN_AGENT_IDS = {"explore"}
MAX_DEPTH = 10


def read_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError(f"{path}: unterminated frontmatter")
    parsed = yaml.safe_load(text[4:end]) or {}
    if not isinstance(parsed, dict):
        raise ValueError(f"{path}: frontmatter must be a mapping")
    return parsed


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def max_depth(graph: dict[str, list[str]]) -> tuple[int, list[str]]:
    memo: dict[str, tuple[int, list[str]]] = {}
    visiting: set[str] = set()

    def dfs(node: str) -> tuple[int, list[str]]:
        if node in memo:
            return memo[node]
        if node in visiting:
            return 0, [node]
        visiting.add(node)
        best_len, best_path = 0, [node]
        for nxt in graph.get(node, []):
            if nxt not in graph:
                if 1 > best_len:
                    best_len, best_path = 1, [node, nxt]
                continue
            sub_len, sub_path = dfs(nxt)
            if sub_len + 1 > best_len:
                best_len = sub_len + 1
                best_path = [node] + sub_path
        visiting.discard(node)
        memo[node] = (best_len, best_path)
        return memo[node]

    result = (0, [])
    for node in graph:
        candidate = dfs(node)
        if candidate[0] > result[0]:
            result = candidate
    return result


def detect_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    color = {node: "white" for node in graph}
    stack: list[str] = []
    cycles: list[list[str]] = []

    def dfs(node: str) -> None:
        color[node] = "grey"
        stack.append(node)
        for nxt in graph.get(node, []):
            if nxt not in color:
                continue
            if color[nxt] == "grey":
                cycles.append(stack[stack.index(nxt) :] + [nxt])
            elif color[nxt] == "white":
                dfs(nxt)
        stack.pop()
        color[node] = "black"

    for node in graph:
        if color[node] == "white":
            dfs(node)
    return cycles


def validate_registry(agent_dir: Path) -> tuple[list[str], dict[str, list[str]]]:
    failures: list[str] = []
    graph: dict[str, list[str]] = {}
    files = sorted(agent_dir.glob("*.md"))
    ids = {path.stem for path in files}

    if not files:
        failures.append(f"no opencode agent files under {agent_dir}")
        return failures, graph

    for path in files:
        agent_id = path.stem
        try:
            frontmatter = read_frontmatter(path)
        except Exception as exc:
            failures.append(str(exc))
            continue

        if frontmatter.get("name") != agent_id:
            failures.append(f"{path.name}: name must be {agent_id!r}")
        if frontmatter.get("mode") != "all":
            failures.append(f"{path.name}: mode must be 'all' for primary + subagent use")
        if not frontmatter.get("description"):
            failures.append(f"{path.name}: missing description")
        if not frontmatter.get("model"):
            failures.append(f"{path.name}: missing model")

        # Read delegates/handoffs from sidecar (preferred) or frontmatter
        sidecar_path = path.with_suffix(".meta.yaml")
        sidecar = {}
        if sidecar_path.is_file():
            sidecar = yaml.safe_load(sidecar_path.read_text(encoding="utf-8")) or {}
        
        delegates = sidecar.get("delegates") if sidecar else None
        if delegates is None:
            delegates = (frontmatter.get("options") or {}).get("delegates") or []
        if not isinstance(delegates, list):
            failures.append(f"{path.name}: delegates must be a list")
            delegates = []

        graph[agent_id] = []
        for delegate in delegates:
            if isinstance(delegate, str):
                delegate_id = delegate
            elif isinstance(delegate, dict):
                delegate_id = delegate.get("id")
            else:
                failures.append(f"{path.name}: delegate entry must be string or object")
                continue
            if not isinstance(delegate_id, str):
                failures.append(f"{path.name}: delegate missing string id")
                continue
            if delegate_id not in ids and delegate_id not in BUILTIN_AGENT_IDS:
                failures.append(f"{path.name}: unknown delegate id {delegate_id!r}")
            graph[agent_id].append(delegate_id)

        handoffs = sidecar.get("handoffs") if sidecar else None
        if handoffs is None:
            handoffs = (frontmatter.get("options") or {}).get("handoffs") or []
        for handoff in handoffs:
            if isinstance(handoff, str):
                handoff_id = handoff
            elif isinstance(handoff, dict):
                handoff_id = handoff.get("id")
            else:
                continue
            if isinstance(handoff_id, str) and handoff_id not in ids and handoff_id not in BUILTIN_AGENT_IDS:
                failures.append(f"{path.name}: unknown handoff id {handoff_id!r}")

    cycles = detect_cycles(graph)
    if cycles:
        failures.append("delegation cycle(s): " + "; ".join(" -> ".join(cycle) for cycle in cycles))

    depth, path = max_depth(graph)
    if depth > MAX_DEPTH:
        failures.append(f"delegation depth {depth} exceeds {MAX_DEPTH}: {' -> '.join(path)}")
    if depth < 2:
        failures.append("delegation graph is not multi-level")

    return failures, graph


def validate_global_mirror(failures: list[str]) -> None:
    project_files = sorted(PROJECT_AGENT_DIR.glob("*.md"))
    global_files = sorted(GLOBAL_AGENT_DIR.glob("*.md"))
    project_ids = {path.stem for path in project_files}
    global_ids = {path.stem for path in global_files}
    missing = sorted(project_ids - global_ids)
    extra = sorted(global_ids - project_ids)
    if missing:
        failures.append(f"global registry missing agents: {', '.join(missing)}")
    if extra:
        failures.append(f"global registry has extra agents: {', '.join(extra)}")
    for project_path in project_files:
        global_path = GLOBAL_AGENT_DIR / project_path.name
        if global_path.exists() and file_hash(project_path) != file_hash(global_path):
            failures.append(f"global registry stale for {project_path.name}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate OpenCode agent registry")
    parser.add_argument(
        "--target",
        choices=["project", "global"],
        default="project",
        help="Registry to validate: project (.opencode/agent) or global (~/.config/opencode/agent)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    agent_dir = GLOBAL_AGENT_DIR if args.target == "global" else PROJECT_AGENT_DIR
    failures, graph = validate_registry(agent_dir)
    if args.target == "global":
        validate_global_mirror(failures)

    if failures:
        print(f"FAIL: {len(failures)} opencode registry issue(s)")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    depth, path = max_depth(graph)
    print(f"PASS: {len(graph)} opencode agents in {agent_dir}")
    print(f"PASS: delegation graph max depth {depth}: {' -> '.join(path)}")
    print("PASS: OpenCode agent registry is internally consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
