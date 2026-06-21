#!/usr/bin/env python3
"""Search the persona's private chat memory with date and context filters."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--query", default="")
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--speaker", choices=("self", "target"))
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--context", type=int, default=2)
    parser.add_argument("--all-types", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def query_terms(raw: str) -> list[str]:
    return re.findall(r"[\w\u3400-\u9fff]+", raw, flags=re.UNICODE)


def main() -> int:
    args = parse_args()
    connection = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    clauses: list[str] = []
    params: list[object] = []

    if not args.all_types:
        clauses.append("m.type = 'text'")
    for term in query_terms(args.query):
        clauses.append("m.message LIKE ?")
        params.append(f"%{term}%")
    if args.start:
        clauses.append("m.datetime >= ?")
        params.append(args.start)
    if args.end:
        clauses.append("m.datetime <= ?")
        params.append(args.end + " 23:59:59" if len(args.end) == 10 else args.end)
    if args.speaker:
        clauses.append("m.speaker = ?")
        params.append(args.speaker)

    hits = connection.execute(
        f"SELECT m.* FROM messages m WHERE {' AND '.join(clauses) or '1=1'} "
        "ORDER BY m.timestamp LIMIT ?",
        (*params, args.limit),
    ).fetchall()
    ids: set[int] = set()
    for hit in hits:
        ids.update(range(max(1, hit["id"] - args.context), hit["id"] + args.context + 1))
    if not ids:
        print("[]" if args.json else "No matching memory evidence.")
        return 0

    placeholders = ",".join("?" for _ in ids)
    type_filter = "" if args.all_types else " AND type = 'text'"
    rows = connection.execute(
        f"SELECT * FROM messages WHERE id IN ({placeholders}){type_filter} "
        "ORDER BY timestamp, id",
        tuple(sorted(ids)),
    ).fetchall()
    output = [dict(row) for row in rows]
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        for row in output:
            label = "她" if row["speaker"] == "target" else "我"
            print(f'{row["datetime"]} [{label}/{row["account"]}] {row["message"]}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
