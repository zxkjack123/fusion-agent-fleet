#!/usr/bin/env python3
"""Validate that every delegated callee exposes an inbound contract.

The checker covers both prose references in an agent's ``## Outbound
Delegation Schemas`` section and OpenCode routing references from
``options.delegates`` and ``options.handoffs``. ``explore`` is an OpenCode
built-in and is the only built-in exemption.

Exit 0 when all references resolve; exit 1 otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
import argparse
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_DIR = REPO_ROOT / ".opencode" / "agent"
BUILTIN_EXEMPTIONS = {"explore", "Explore"}

OUTBOUND_HEADING = re.compile(r"^## Outbound Delegation Schemas\s*$", re.MULTILINE)
NEXT_H2 = re.compile(r"^## ", re.MULTILINE)
CALLEE_REF = re.compile(
    r"\(see\s+`(?:\.opencode/agent/)?([a-z0-9-]+\.md)`\s*→\s*`### 调用方需提供`\)"
)
INBOUND_HEADING = re.compile(
    r"^### 调用方需提供(?:（[^）]*）)?\s*$", re.MULTILINE
)
INLINE_LIST_RE = re.compile(r"\[(.*)\]")
QUOTED_ITEM_RE = re.compile(r'"([^"]+)"')
NAME_LINE = re.compile(r'^name:\s*"?([^"\n]+?)"?\s*$', re.MULTILINE)


def extract_outbound_section(text: str) -> str | None:
    m = OUTBOUND_HEADING.search(text)
    if not m:
        return None
    start = m.end()
    nxt = NEXT_H2.search(text, start)
    end = nxt.start() if nxt else len(text)
    return text[start:end]


def read_frontmatter(path: Path) -> str:
    """Return YAML frontmatter from an agent file."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 4)
    if end == -1:
        return text
    return text[: end + 4]


def read_frontmatter_dict(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    parsed = yaml.safe_load(text[4:end]) or {}
    return parsed if isinstance(parsed, dict) else {}


def parse_name(frontmatter: str) -> str:
    """Extract the agent display name from frontmatter."""
    match = NAME_LINE.search(frontmatter)
    return match.group(1) if match else ""


def parse_list(frontmatter: str, key: str) -> list[str]:
    """Parse inline or block-form YAML lists from frontmatter."""
    lines = frontmatter.splitlines()
    items: list[str] = []
    in_block = False
    for line in lines:
        stripped = line.rstrip()
        if not in_block:
            if stripped.startswith(f"{key}:"):
                rest = stripped[len(key) + 1:].strip()
                if rest.startswith("["):
                    inline = INLINE_LIST_RE.search(stripped)
                    if inline:
                        items.extend(QUOTED_ITEM_RE.findall(inline.group(1)))
                    return items
                if rest == "":
                    in_block = True
                    continue
                return items
            continue
        if line.startswith("  - "):
            items.append(line[4:].strip().strip('"'))
            continue
        if stripped and not line.startswith(" "):
            break
    return items


def parse_handoff_agents(frontmatter: str) -> list[str]:
    """Parse target agent names from frontmatter ``handoffs:`` entries."""
    lines = frontmatter.splitlines()
    items: list[str] = []
    in_handoffs = False
    for line in lines:
        stripped = line.rstrip()
        if not in_handoffs:
            if stripped.startswith("handoffs:"):
                in_handoffs = True
            continue
        if stripped and not line.startswith(" "):
            break
        match = re.match(r'^\s+agent:\s*"?([^"\n]+?)"?\s*$', line)
        if match:
            items.append(match.group(1))
    return items


def read_sidecar_dict(path: Path) -> dict:
    """Load sidecar .meta.yaml as a dict."""
    sidecar = path.with_suffix(".meta.yaml")
    if sidecar.is_file():
        data = yaml.safe_load(sidecar.read_text(encoding="utf-8")) or {}
        return data if isinstance(data, dict) else {}
    return {}


def parse_delegate_ids(frontmatter: dict, sidecar: dict | None = None) -> list[str]:
    """Parse delegate ids from sidecar (preferred) or frontmatter options."""
    source = sidecar if sidecar is not None else {}
    if not source:
        options = frontmatter.get("options") or {}
        source = options
    result: list[str] = []
    for item in source.get("delegates") or []:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            result.append(item["id"])
        elif isinstance(item, str):
            result.append(item)
    return result


def parse_handoff_ids(frontmatter: dict, sidecar: dict | None = None) -> list[str]:
    """Parse handoff ids from sidecar (preferred) or frontmatter options."""
    source = sidecar if sidecar is not None else {}
    if not source:
        options = frontmatter.get("options") or {}
        source = options
    result: list[str] = []
    for item in source.get("handoffs") or []:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            result.append(item["id"])
        elif isinstance(item, str):
            result.append(item)
    return result


def collect_agent_metadata(agent_files: list[Path]) -> dict[str, dict]:
    """Return metadata keyed by OpenCode agent id."""
    metadata: dict[str, dict] = {}
    for agent_file in agent_files:
        frontmatter = read_frontmatter_dict(agent_file)
        sidecar = read_sidecar_dict(agent_file)
        name = frontmatter.get("name") or agent_file.stem
        if not name:
            continue
        metadata[name] = {
            "path": agent_file,
            "agents": parse_delegate_ids(frontmatter, sidecar),
            "handoffs": parse_handoff_ids(frontmatter, sidecar),
        }
    return metadata


def file_for_agent_name(name: str) -> str:
    """Return conventional agent filename for diagnostics."""
    return f"{name.lower().replace(' ', '-')}.md"


def load_sidecar(agent_file: Path) -> str:
    """Load sidecar metadata text for an agent file.

    Returns the concatenated text of outbound_schemas_text and
    inbound_contract_text from the .meta.yaml sidecar, or the agent
    body text itself if no sidecar exists (backward compat).
    """
    sidecar = agent_file.with_suffix(".meta.yaml")
    if sidecar.is_file():
        import yaml as _yaml
        data = _yaml.safe_load(sidecar.read_text(encoding="utf-8")) or {}
        parts = []
        for key in ("inbound_contract_text", "outbound_schemas_text", "return_envelope_text"):
            val = data.get(key)
            if val:
                parts.append(val)
        if parts:
            return "\n\n".join(parts)
    # Fallback: read agent body
    return agent_file.read_text(encoding="utf-8")


def iter_contract_refs(agent_files: list[Path]) -> list[tuple[str, str, str]]:
    """Return ``(source_file, kind, callee_file)`` contract references."""
    refs: list[tuple[str, str, str]] = []
    metadata = collect_agent_metadata(agent_files)

    for agent_file in agent_files:
        sidecar_text = load_sidecar(agent_file)
        section = extract_outbound_section(sidecar_text)
        if section is not None:
            for callee in CALLEE_REF.findall(section):
                refs.append((agent_file.name, "schema", callee))

        frontmatter = read_frontmatter_dict(agent_file)
        sidecar = read_sidecar_dict(agent_file)
        caller_name = frontmatter.get("name") or agent_file.stem
        if not caller_name:
            continue
        for callee_name in parse_delegate_ids(frontmatter, sidecar):
            if callee_name in BUILTIN_EXEMPTIONS:
                continue
            callee = metadata.get(callee_name, {}).get(
                "path", Path(file_for_agent_name(callee_name))
            ).name
            refs.append((agent_file.name, "frontmatter:delegates", callee))
        for callee_name in parse_handoff_ids(frontmatter, sidecar):
            if callee_name in BUILTIN_EXEMPTIONS:
                continue
            callee = metadata.get(callee_name, {}).get(
                "path", Path(file_for_agent_name(callee_name))
            ).name
            refs.append((agent_file.name, "frontmatter:handoffs", callee))

    return refs


def check_outbound_coverage(agent_files: list[Path]) -> list[str]:
    """Return list of failure messages for agents missing outbound schemas.

    An agent needs outbound schemas in its sidecar if it has non-empty
    delegates or handoffs in frontmatter.  Leaf agents are also required
    to have an explicit N/A section.
    """
    failures: list[str] = []
    for agent_file in agent_files:
        frontmatter = read_frontmatter_dict(agent_file)
        sidecar = read_sidecar_dict(agent_file)
        agents_list = parse_delegate_ids(frontmatter, sidecar)
        handoff_list = parse_handoff_ids(frontmatter, sidecar)
        has_delegation = bool(agents_list or handoff_list)

        sidecar_text = load_sidecar(agent_file)
        has_outbound = OUTBOUND_HEADING.search(sidecar_text) is not None

        if not has_outbound:
            if has_delegation:
                failures.append(
                    f"{agent_file.name}: has delegates/handoffs in sidecar "
                    f"but missing `## Outbound Delegation Schemas` in sidecar"
                )
            else:
                failures.append(
                    f"{agent_file.name}: leaf agent missing explicit "
                    f"`## Outbound Delegation Schemas` (N/A) in sidecar"
                )
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate delegation contract references across agent fleet"
    )
    parser.add_argument(
        "--require-outbound-coverage",
        action="store_true",
        default=False,
        help="Require agents with handoffs/agents to have outbound "
             "delegation pattern section (default: off)",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        default=False,
        help="Print warnings instead of failing (exit 0 always)",
    )
    return parser.parse_args()


def main(args: argparse.Namespace) -> int:
    failures: list[str] = []
    checked_refs = 0
    agent_files = sorted(AGENT_DIR.glob("*.md"))

    for source_file, kind, callee in iter_contract_refs(agent_files):
        checked_refs += 1
        callee_path = AGENT_DIR / callee
        if not callee_path.is_file():
            failures.append(
                f"{source_file} [{kind}] → {callee}: callee file not found"
            )
            continue
        callee_sidecar_text = load_sidecar(callee_path)
        if not INBOUND_HEADING.search(callee_sidecar_text):
            failures.append(
                f"{source_file} [{kind}] → {callee}: missing "
                f"`### 调用方需提供` heading in callee sidecar"
            )

    if args.require_outbound_coverage:
        outbound_failures = check_outbound_coverage(agent_files)
        failures.extend(outbound_failures)

    if failures:
        if args.warn_only:
            print(f"WARN: {len(failures)} delegation contract mismatch(es):")
            for line in failures:
                print(f"  - {line}")
            print(f"(checked {checked_refs} reference(s))")
            return 0
        else:
            print(f"FAIL: {len(failures)} delegation contract mismatch(es):")
            for line in failures:
                print(f"  - {line}")
            print(f"(checked {checked_refs} reference(s))")
            return 1

    print(f"PASS: {checked_refs} delegation reference(s) resolved")
    return 0


if __name__ == "__main__":
    sys.exit(main(parse_args()))
