#!/usr/bin/env python3
"""Unified State Manager API — single entrypoint for checkpoint, span, findings, claims.

Usage:
  python3 scripts/state_api.py --mode write_checkpoint [args...]
  python3 scripts/state_api.py --mode read_checkpoint [args...]
  python3 scripts/state_api.py --mode is_completed [args...]
  python3 scripts/state_api.py --mode extract_claims < input_text
  python3 scripts/state_api.py --mode write_finding [args...]
  python3 scripts/state_api.py --mode query_span [args...]
"""

import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACES_DIR = REPO_ROOT / "traces"
CHECKPOINT_FILE = TRACES_DIR / "checkpoint.json"
TRACE_DB = TRACES_DIR / "trace.db"
PROJECTS_DIR = REPO_ROOT / "projects"


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ─── Checkpoint Operations ───────────────────────────────────────

def write_checkpoint(args):
    """Append a checkpoint entry to traces/checkpoint.json (JSONL)."""
    entry = {
        "plan": args.plan,
        "task_id": args.task_id,
        "trace_id": args.trace_id,
        "status": args.status,
        "git_commit": args.git_commit,
        "files_modified": json.loads(args.files) if args.files else [],
        "started_at": args.started_at or utcnow(),
        "completed_at": utcnow(),
        "duration_ms": args.duration_ms,
        "token_input": args.token_input,
        "token_output": args.token_output,
    }
    if args.error_compact:
        entry["error_compact"] = json.loads(args.error_compact)

    TRACES_DIR.mkdir(parents=True, exist_ok=True)

    # Idempotency: check if this task is already COMPLETED
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    existing = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if (existing.get("plan") == args.plan
                        and existing.get("task_id") == args.task_id
                        and existing.get("status") == "COMPLETED"):
                    print(json.dumps({"skipped": True, "reason": "already COMPLETED"}))
                    return
                # Also skip duplicate FAILED entries for same task
                if (existing.get("plan") == args.plan
                        and existing.get("task_id") == args.task_id
                        and existing.get("status") == args.status):
                    print(json.dumps({"skipped": True, "reason": f"already {args.status}"}))
                    return

    with open(CHECKPOINT_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps({"written": True, "task_id": args.task_id}))


def read_checkpoint(args):
    """Read checkpoint entries for a plan, optionally filtered by task_id."""
    if not CHECKPOINT_FILE.exists():
        print(json.dumps({"results": [], "plan": args.plan}))
        return
    results = []
    with open(CHECKPOINT_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("plan") == args.plan:
                if args.task_id and entry.get("task_id") != args.task_id:
                    continue
                results.append(entry)
    print(json.dumps({"results": results, "plan": args.plan, "count": len(results)}))


def is_completed(args):
    """Check if a specific task is completed."""
    if not CHECKPOINT_FILE.exists():
        print(json.dumps({"completed": False, "plan": args.plan, "task_id": args.task_id}))
        return
    with open(CHECKPOINT_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if (entry.get("plan") == args.plan
                    and entry.get("task_id") == args.task_id):
                print(json.dumps({
                    "completed": entry.get("status") == "COMPLETED",
                    "plan": args.plan,
                    "task_id": args.task_id,
                    "status": entry.get("status"),
                }))
                return
    print(json.dumps({"completed": False, "plan": args.plan, "task_id": args.task_id, "status": "NOT_FOUND"}))


# ─── Claim Extraction ────────────────────────────────────────────

QUANT_CLAIM_RE = re.compile(
    r"(\d+\.?\d*)\s*±\s*(\d+\.?\d*)\s*"  # value ± uncertainty
    r"(MW|GW|kW|W|MeV|keV|eV|K|°C|Sv|Gy|mSv|μSv|"
    r"Bq|Ci|kg|g|mg|Pa|MPa|GPa|m|cm|mm|nm|m[²³]|cm[²³]|"
    r"W/m[²³]|MW/m[²³])"  # unit
    r"(?:[^.]*?(?:CONFIRMED|VERIFIED|within\s+1σ|matches\s+literature))?",  # verdict (optional)
    re.IGNORECASE
)

SIMPLE_CLAIM_RE = re.compile(
    r"(\d+\.?\d*)\s*(MW|GW|kW|W|MeV|keV|K|Sv|Gy|mSv|μSv|TBR)",
    re.IGNORECASE
)


def extract_claims(args):
    """Extract quantitative claims from stdin text."""
    text = sys.stdin.read()
    claims = []

    for m in QUANT_CLAIM_RE.finditer(text):
        value = float(m.group(1))
        uncertainty = float(m.group(2))
        unit = m.group(3)
        start = max(0, m.start() - 40)
        end = min(len(text), m.end() + 80)
        context = text[start:end].replace("\n", " ").strip()[:200]
        verdict = "CONFIRMED" if any(kw in m.group(0).lower() for kw in ["confirmed", "verified", "within 1σ", "matches literature"]) else "UNVERIFIED"
        claims.append({
            "value": value,
            "uncertainty": uncertainty,
            "unit": unit,
            "context": context,
            "verdict": verdict,
        })

    # Fallback: simple value+unit without uncertainty
    if not claims:
        for m in SIMPLE_CLAIM_RE.finditer(text):
            value = float(m.group(1))
            unit = m.group(2)
            start = max(0, m.start() - 40)
            end = min(len(text), m.end() + 80)
            context = text[start:end].replace("\n", " ").strip()[:200]
            claims.append({
                "value": value,
                "uncertainty": None,
                "unit": unit,
                "context": context,
                "verdict": "UNVERIFIED",
            })

    print(json.dumps({"claims": claims, "count": len(claims)}))


# ─── Findings Ledger ─────────────────────────────────────────────

def write_finding(args):
    """Write a finding to projects/<project>/findings/<date>-<seq>.yaml."""
    project_dir = PROJECTS_DIR / args.project
    findings_dir = project_dir / "findings"
    findings_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now(timezone.utc).strftime("%Y%m%d")

    # Find next sequence number
    existing = sorted(findings_dir.glob(f"{today}-*.yaml"))
    if existing:
        last_seq = int(existing[-1].stem.split("-")[-1])
        next_seq = last_seq + 1
    else:
        next_seq = 1

    seq_id = f"{next_seq:03d}"
    filename = f"{today}-{seq_id}.yaml"
    filepath = findings_dir / filename

    finding_data = json.loads(args.finding) if args.finding else {}
    finding_data["finding_id"] = f"f-{today}-{seq_id}"
    finding_data["project"] = args.project

    # Write as YAML-like key-value (simple format)
    with open(filepath, "w") as f:
        for key, value in finding_data.items():
            if isinstance(value, list):
                f.write(f"{key}:\n")
                for item in value:
                    f.write(f"  - {item}\n")
            else:
                f.write(f"{key}: {value}\n")

    print(json.dumps({"written": True, "path": str(filepath), "finding_id": finding_data["finding_id"]}))


# ─── Span Query ──────────────────────────────────────────────────

def query_span(args):
    """Query span information via trace_query.py SQLite backend."""
    if not TRACE_DB.exists():
        print(json.dumps({"error": "trace db not found. Run: python3 scripts/trace_query.py --ingest"}))
        return

    import sqlite3
    conn = sqlite3.connect(str(TRACE_DB))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT span_id, parent_span_id, agent_name, task_description, status,
               error_type, duration_ms, token_usage, decision_rationale, timestamp
        FROM spans
        WHERE trace_id = ?
        ORDER BY timestamp
    """, (args.trace_id,))

    spans = [dict(row) for row in cursor.fetchall()]
    conn.close()

    print(json.dumps({"trace_id": args.trace_id, "spans": spans, "count": len(spans)}))


# ─── CLI ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Unified State Manager API")
    parser.add_argument("--mode", required=True, choices=[
        "write_checkpoint", "read_checkpoint", "is_completed",
        "extract_claims", "write_finding", "query_span",
    ])

    # Checkpoint args
    parser.add_argument("--plan", help="Plan name")
    parser.add_argument("--task-id", help="Task ID")
    parser.add_argument("--trace-id", default=lambda: str(uuid.uuid4()), help="Trace ID")
    parser.add_argument("--status", help="Task status (COMPLETED|FAILED|BLOCKED)")
    parser.add_argument("--git-commit", help="Git commit hash")
    parser.add_argument("--files", help="JSON array of modified file paths")
    parser.add_argument("--started-at", help="ISO8601 start time")
    parser.add_argument("--duration-ms", type=int, help="Duration in milliseconds")
    parser.add_argument("--token-input", type=int, help="Input tokens")
    parser.add_argument("--token-output", type=int, help="Output tokens")
    parser.add_argument("--error-compact", help="JSON error compact dict")

    # Finding args
    parser.add_argument("--project", help="Project name")
    parser.add_argument("--finding", help="JSON finding dict")

    args = parser.parse_args()

    mode_handlers = {
        "write_checkpoint": write_checkpoint,
        "read_checkpoint": read_checkpoint,
        "is_completed": is_completed,
        "extract_claims": extract_claims,
        "write_finding": write_finding,
        "query_span": query_span,
    }

    handler = mode_handlers.get(args.mode)
    if handler:
        handler(args)
    else:
        print(f"Unknown mode: {args.mode}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
