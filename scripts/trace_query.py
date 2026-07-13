#!/usr/bin/env python3
"""Query and manage agent execution trace data.

Reads trace JSONL from `traces/trace.jsonl`, ingests into SQLite for
efficient querying, and supports live monitoring and rotation.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACE_DIR = REPO_ROOT / "traces"
DEFAULT_JSONL = TRACE_DIR / "trace.jsonl"
DEFAULT_DB = TRACE_DIR / "trace.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS spans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT NOT NULL,
    parent_span_id TEXT,
    span_id TEXT NOT NULL UNIQUE,
    agent_name TEXT NOT NULL,
    model TEXT,
    task_description TEXT NOT NULL,
    status TEXT NOT NULL,
    error_type TEXT,
    duration_ms INTEGER,
    token_input INTEGER,
    token_output INTEGER,
    token_reasoning INTEGER,
    decision_rationale TEXT,
    routing_path TEXT,
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_spans_trace_id ON spans(trace_id);
CREATE INDEX IF NOT EXISTS idx_spans_agent ON spans(agent_name);
CREATE INDEX IF NOT EXISTS idx_spans_status ON spans(status);
CREATE INDEX IF NOT EXISTS idx_spans_timestamp ON spans(timestamp);
"""


def ensure_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def ingest_jsonl(jsonl_path: Path, db_path: Path) -> int:
    if not jsonl_path.is_file():
        print(f"  [SKIP] {jsonl_path} not found", file=sys.stderr)
        return 0

    conn = ensure_db(db_path)
    count = 0
    skipped = 0
    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                span = json.loads(line)
            except json.JSONDecodeError:
                skipped += 1
                continue

            token = span.get("token_usage") or {}
            try:
                conn.execute(
                    """INSERT OR REPLACE INTO spans
                       (trace_id, parent_span_id, span_id, agent_name, model,
                        task_description, status, error_type, duration_ms,
                        token_input, token_output, token_reasoning,
                        decision_rationale, routing_path, timestamp)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        span["trace_id"],
                        span.get("parent_span_id"),
                        span["span_id"],
                        span.get("agent_name", "unknown"),
                        span.get("model"),
                        span.get("task_description", ""),
                        span.get("status", "UNKNOWN"),
                        span.get("error_type"),
                        span.get("duration_ms"),
                        token.get("input"),
                        token.get("output"),
                        token.get("reasoning"),
                        span.get("decision_rationale"),
                        span.get("routing_path"),
                        span.get("timestamp", ""),
                    ),
                )
                count += 1
            except sqlite3.IntegrityError:
                skipped += 1

    conn.commit()
    print(f"  Ingested {count} spans, skipped {skipped} (duplicates)")
    return count


def query_agent(conn: sqlite3.Connection, agent: str, since_days: int | None):
    where = "WHERE agent_name = ?"
    params: list = [agent]
    if since_days:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=since_days)).isoformat()
        where += " AND timestamp >= ?"
        params.append(cutoff)
    rows = conn.execute(
        f"SELECT span_id, task_description, status, duration_ms, "
        f"token_input, token_output, token_reasoning, timestamp "
        f"FROM spans {where} ORDER BY timestamp DESC LIMIT 50",
        params,
    ).fetchall()
    if not rows:
        print(f"No spans found for agent '{agent}'")
        sys.exit(1)
    print(f"{'SPAN_ID':<30} {'TASK':<40} {'STATUS':<10} {'DUR(ms)':>8} {'IN':>6} {'OUT':>6} {'RSN':>6}")
    print("-" * 120)
    for r in rows:
        print(f"{r[0]:<30} {r[1][:38]:<40} {r[2]:<10} {r[3] or 0:>8} {r[4] or 0:>6} {r[5] or 0:>6} {r[6] or 0:>6}")


def query_error_rate(conn: sqlite3.Connection, since_days: int | None):
    clauses = ["status != 'STARTED'"]
    params: list = []
    if since_days:
        clauses.append("timestamp >= ?")
        params.append((datetime.now(timezone.utc) - timedelta(days=since_days)).isoformat())
    where_clause = " AND ".join(clauses)
    rows = conn.execute(
        f"""SELECT agent_name,
                   COUNT(*) as total,
                   SUM(CASE WHEN status IN ('FAILED','BLOCKED') THEN 1 ELSE 0 END) as failed,
                   ROUND(AVG(duration_ms)) as avg_ms,
                   SUM(token_input) as tot_in,
                   SUM(token_output) as tot_out
            FROM spans
            WHERE {where_clause}
            GROUP BY agent_name
            ORDER BY total DESC""",
        params,
    ).fetchall()
    if not rows:
        print("No completed spans found")
        sys.exit(1)
    print(f"{'AGENT':<30} {'TOTAL':>6} {'FAILED':>7} {'ERR%':>6} {'AVG_MS':>8} {'TOT_IN':>8} {'TOT_OUT':>8}")
    print("-" * 90)
    for r in rows:
        rate = f"{r[2]/r[1]*100:.1f}%" if r[1] > 0 else "0%"
        print(f"{r[0]:<30} {r[1]:>6} {r[2]:>7} {rate:>6} {r[3] or 0:>8} {r[4] or 0:>8} {r[5] or 0:>8}")


def query_top_cost(conn: sqlite3.Connection, since_days: int | None):
    clauses = ["status != 'STARTED'"]
    params: list = []
    if since_days:
        clauses.append("timestamp >= ?")
        params.append((datetime.now(timezone.utc) - timedelta(days=since_days)).isoformat())
    where_clause = " AND ".join(clauses)
    rows = conn.execute(
        f"""SELECT agent_name, trace_id,
                   SUM(token_input) as tot_in,
                   SUM(token_output) as tot_out,
                   SUM(token_reasoning) as tot_reason,
                   COUNT(*) as spans
            FROM spans
            WHERE {where_clause}
            GROUP BY agent_name, trace_id
            ORDER BY (SUM(token_input) + SUM(token_output) + SUM(token_reasoning)) DESC
            LIMIT 20""",
        params,
    ).fetchall()
    if not rows:
        print("No token data found")
        sys.exit(1)
    print(f"{'AGENT':<30} {'TRACE_ID':<30} {'IN':>8} {'OUT':>8} {'REASON':>8} {'TOTAL':>8} {'SPANS':>6}")
    print("-" * 105)
    for r in rows:
        total = (r[2] or 0) + (r[3] or 0) + (r[4] or 0)
        print(f"{r[0]:<30} {r[1]:<30} {r[2] or 0:>8} {r[3] or 0:>8} {r[4] or 0:>8} {total:>8} {r[5]:>6}")


def query_span_tree(conn: sqlite3.Connection, trace_id: str):
    rows = conn.execute(
        """SELECT span_id, parent_span_id, agent_name, status, duration_ms,
                  token_input, token_output, token_reasoning, decision_rationale, timestamp
           FROM spans WHERE trace_id = ? ORDER BY timestamp""",
        (trace_id,),
    ).fetchall()
    if not rows:
        print(f"No spans found for trace_id '{trace_id}'")
        sys.exit(1)
    children: dict[str, list] = {}
    by_id = {}
    for r in rows:
        by_id[r[0]] = r
        parent = r[1] if r[1] else "__root__"
        children.setdefault(parent, []).append(r)
    root_ids = set(r[0] for r in rows) - {r[1] for r in rows if r[1]}

    def print_tree(node_id: str | None, indent: int, is_last: bool, parent_prefix: str):
        if node_id is None:
            # root children
            for i, rid in enumerate(sorted(root_ids)):
                r = by_id[rid]
                print_tree(rid, indent, i == len(root_ids) - 1, "")
        else:
            r = by_id[node_id]
            branch = "└── " if is_last else "├── "
            status_mark = {"SUCCESS": "✅", "FAILED": "❌", "BLOCKED": "🛑", "SKIPPED": "⏸", "STARTED": "▶️"}.get(r[3], "❓")
            dur = f" ({r[4]}ms)" if r[4] else ""
            tokens = f" [in={r[5] or 0}, out={r[6] or 0}]" if r[5] or r[6] else ""
            rationale = f" → {r[8][:60]}..." if len(r) > 8 and r[8] else ""
            print(f"{parent_prefix}{branch}{status_mark} {r[2]} — {r[3]}{dur}{tokens}{rationale}")
            child_list = children.get(node_id, [])
            child_list.sort(key=lambda x: x[9] or "")  # sort by timestamp (index 9)
            for i, child in enumerate(child_list):
                new_prefix = parent_prefix + ("    " if is_last else "│   ")
                print_tree(child[0], indent + 1, i == len(child_list) - 1, new_prefix)

    for rid in sorted(root_ids):
        print_tree(rid, 0, False, "")


def do_live(jsonl_path: Path, interval_sec: int = 2):
    if not jsonl_path.is_file():
        print(f"Waiting for {jsonl_path}...")
    try:
        last_size = jsonl_path.stat().st_size if jsonl_path.is_file() else 0
        while True:
            if jsonl_path.is_file():
                current_size = jsonl_path.stat().st_size
                if current_size > last_size:
                    with open(jsonl_path) as f:
                        f.seek(last_size)
                        for line in f:
                            line = line.strip()
                            if line:
                                try:
                                    span = json.loads(line)
                                    status_mark = {"STARTED": "▶️", "SUCCESS": "✅", "FAILED": "❌", "BLOCKED": "🛑", "SKIPPED": "⏸"}.get(span.get("status", ""), "❓")
                                    agent = span.get("agent_name", "?")
                                    task = span.get("task_description", "?")
                                    dur = f" ({span['duration_ms']}ms)" if span.get("duration_ms") else ""
                                    print(f"[{span.get('timestamp', '?')}] {status_mark} {agent} | {task}{dur}")
                                except json.JSONDecodeError:
                                    pass
                    last_size = current_size
            time.sleep(interval_sec)
    except KeyboardInterrupt:
        print("\nLive monitoring stopped.")


def do_rotate(jsonl_path: Path, keep_days: int):
    if not jsonl_path.is_file():
        print(f"No {jsonl_path} to rotate")
        return
    archive_dir = jsonl_path.parent / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = archive_dir / f"trace-{ts}.jsonl.gz"
    try:
        with open(jsonl_path) as f_in, gzip.open(dest, "wt") as f_out:
            f_out.write(f_in.read())
        jsonl_path.unlink()
        print(f"  Archived → {dest}")
    except (OSError, gzip.BadGzipFile) as e:
        print(f"  gzip failed ({e}), falling back to truncate")
        jsonl_path.unlink()
        print(f"  Truncated {jsonl_path}")

    # cleanup old archives
    cutoff = datetime.now() - timedelta(days=keep_days)
    for f in sorted(archive_dir.glob("trace-*.jsonl.gz")):
        try:
            ts_str = f.stem.replace("trace-", "").split(".")[0]
            ftime = datetime.strptime(ts_str, "%Y%m%d-%H%M%S")
            if ftime < cutoff:
                f.unlink()
                print(f"  Removed old archive: {f.name}")
        except (ValueError, OSError):
            pass


def main():
    parser = argparse.ArgumentParser(description="Agent trace query tool")
    parser.add_argument("--ingest", action="store_true", help="Ingest JSONL into SQLite")
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL, help="JSONL file path (default: traces/trace.jsonl)")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="SQLite DB path (default: traces/trace.db)")
    parser.add_argument("--agent", type=str, help="Query spans for a specific agent")
    parser.add_argument("--error-rate", action="store_true", help="Show per-agent error rate")
    parser.add_argument("--top-cost", action="store_true", help="Show top token-consuming traces")
    parser.add_argument("--span-tree", type=str, metavar="TRACE_ID", help="Reconstruct span tree for a trace")
    parser.add_argument("--since", type=int, metavar="DAYS", help="Filter to last N days")
    parser.add_argument("--live", action="store_true", help="Live tail trace.jsonl")
    parser.add_argument("--rotate", action="store_true", help="Archive trace.jsonl and start fresh")
    parser.add_argument("--keep-days", type=int, default=90, help="Days to keep archived traces (default: 90)")
    args = parser.parse_args()

    if args.rotate:
        do_rotate(args.jsonl, args.keep_days)
        return

    if args.live:
        do_live(args.jsonl)
        return

    if args.ingest:
        ingest_jsonl(args.jsonl, args.db)
        return

    if not args.db.is_file():
        print(f"No trace database at {args.db}. Run --ingest first.", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(str(args.db))

    if args.agent:
        query_agent(conn, args.agent, args.since)
    elif args.error_rate:
        query_error_rate(conn, args.since)
    elif args.top_cost:
        query_top_cost(conn, args.since)
    elif args.span_tree:
        query_span_tree(conn, args.span_tree)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
