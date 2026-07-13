#!/usr/bin/env python3
"""Static checker for the OpenCode agent delegation graph."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
BUILTIN_AGENTS = {"explore"}
KNOWN_MODELS = {
    "fallback/fallback",
    "fallback/deepseek-v4-pro",
    "fallback/deepseek-v4-pro-thinking",
    "fallback/deepseek-v4-flash",
    "fallback/gpt-5.5-high",
    "fallback/claude-opus-4-7",
    "fallback/qwen-flash",
    "deepseek/deepseek-v4-pro",
    "deepseek/deepseek-v4-flash",
    "uiuiapi/claude-opus-4-7",
    "uiuiapi/gpt-5.5-high",
    "scnet/Kimi-K2.6",
    "scnet/MiniMax-M3",
    "scnet/Qwen3.6-Flash",
    "scnet/Qwen3.6-Max",
    "scnet/Qwen3.6-Plus",
    "ollama/minicpm-v:8b",
    "ollama/llama3.2-vision:11b",
    "ollama/llava:7b",
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


def read_sidecar(path: Path) -> dict:
    """Load sidecar .meta.yaml as a dict."""
    sidecar = path.with_suffix(".meta.yaml")
    if sidecar.is_file():
        import yaml as _yaml
        data = _yaml.safe_load(sidecar.read_text(encoding="utf-8")) or {}
        return data if isinstance(data, dict) else {}
    return {}


def parse_agent_file(path: Path) -> dict:
    frontmatter = read_frontmatter(path)
    sidecar = read_sidecar(path)

    # Read delegates/handoffs from sidecar (preferred) or frontmatter
    delegates_source = sidecar.get("delegates") if sidecar else None
    if not delegates_source:
        delegates_source = (frontmatter.get("options") or {}).get("delegates") or []

    handoffs_source = sidecar.get("handoffs") if sidecar else None
    if not handoffs_source:
        handoffs_source = (frontmatter.get("options") or {}).get("handoffs") or []

    delegates = []
    for item in delegates_source:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            delegates.append(item["id"])
        elif isinstance(item, str):
            delegates.append(item)

    handoffs = []
    for item in handoffs_source:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            handoffs.append(item["id"])
        elif isinstance(item, str):
            handoffs.append(item)

    model = frontmatter.get("model")
    return {
        "path": path.name,
        "name": frontmatter.get("name") or path.stem,
        "agents": delegates,
        "handoffs": handoffs,
        "models": [model] if isinstance(model, str) else (model or []),
    }


def detect_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    white, grey, black = 0, 1, 2
    color = {node: white for node in graph}
    stack: list[str] = []
    cycles: list[list[str]] = []

    def dfs(node: str) -> None:
        color[node] = grey
        stack.append(node)
        for nxt in graph.get(node, []):
            if nxt not in color:
                continue
            if color[nxt] == grey:
                cycles.append(stack[stack.index(nxt):] + [nxt])
            elif color[nxt] == white:
                dfs(nxt)
        stack.pop()
        color[node] = black

    for node in graph:
        if color[node] == white:
            dfs(node)
    return cycles


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


def agent_files(repo_root: Path) -> list[Path]:
    agent_dir = repo_root / ".opencode" / "agent"
    if agent_dir.is_dir():
        return sorted(agent_dir.glob("*.md"))
    return sorted(repo_root.glob("*.md"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-agents", type=int, default=48)
    parser.add_argument("--max-depth", type=int, default=10)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    agents = [parse_agent_file(path) for path in agent_files(args.repo_root)]
    by_name = {agent["name"]: agent for agent in agents if agent["name"]}
    pass_count = warn_count = fail_count = 0

    def pass_(msg: str) -> None:
        nonlocal pass_count
        pass_count += 1
        print(f"  ✅ PASS: {msg}")

    def warn(msg: str) -> None:
        nonlocal warn_count
        warn_count += 1
        print(f"  ⚠️  WARN: {msg}")

    def fail(msg: str) -> None:
        nonlocal fail_count
        fail_count += 1
        print(f"  ❌ FAIL: {msg}")

    print(f"Scanning {len(agents)} OpenCode agents under {args.repo_root}\n")

    print(f"Check 1: Agent count (cap = {args.max_agents})")
    if len(agents) > args.max_agents:
        warn(f"agent count {len(agents)} exceeds cap {args.max_agents}")
    else:
        pass_(f"agent count {len(agents)} within cap {args.max_agents}")

    print("\nCheck 2: Model allowlist")
    bad_models = 0
    for agent in agents:
        if not agent["models"]:
            warn(f"{agent['path']} — no model declared")
            continue
        for model in agent["models"]:
            if model not in KNOWN_MODELS:
                warn(f"{agent['path']} — unknown model: {model!r}")
                bad_models += 1
    if bad_models == 0:
        pass_("all model entries are in KNOWN_MODELS")

    graph: dict[str, list[str]] = {}
    handoff_edges: list[tuple[str, str]] = []
    for agent in agents:
        graph.setdefault(agent["name"], [])
        for target in agent["agents"]:
            graph[agent["name"]].append(target)
            graph.setdefault(target, [])
        for target in agent["handoffs"]:
            handoff_edges.append((agent["name"], target))

    print("\nCheck 3: Delegation and handoff target validity")
    unknown_targets = 0
    for src, targets in graph.items():
        for target in targets:
            if target not in by_name and target not in BUILTIN_AGENTS:
                fail(f"{src} --active--> {target} (unknown agent)")
                unknown_targets += 1
    for src, target in handoff_edges:
        if target not in by_name and target not in BUILTIN_AGENTS:
            fail(f"{src} --handoff--> {target} (unknown agent)")
            unknown_targets += 1
    if unknown_targets == 0:
        pass_("all active and handoff targets resolve to known agents or built-ins")

    print("\nCheck 4: Active cycle detection")
    cycles = detect_cycles(graph)
    if cycles:
        for cycle in cycles:
            fail("cycle detected: " + " -> ".join(cycle))
    else:
        pass_("no cycles in active delegation graph")

    print(f"\nCheck 5: Max active delegation depth (limit = {args.max_depth})")
    depth, path = max_depth(graph)
    if depth > args.max_depth:
        warn(f"max depth {depth} exceeds limit {args.max_depth}: " + " -> ".join(path))
    else:
        pass_(f"max depth {depth} within limit {args.max_depth} (longest: {' -> '.join(path)})")

    print(f"\nSummary: {pass_count} PASS, {warn_count} WARN, {fail_count} FAIL")
    if fail_count:
        return 2
    if warn_count:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
