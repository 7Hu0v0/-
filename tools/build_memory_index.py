#!/usr/bin/env python3
"""Build a private SQLite FTS index from a merged WeChat JSONL export."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    timestamp INTEGER NOT NULL,
    datetime TEXT NOT NULL,
    speaker TEXT NOT NULL,
    type TEXT NOT NULL,
    message TEXT NOT NULL,
    account TEXT,
    user_id TEXT,
    server_id TEXT,
    local_id TEXT
);
CREATE VIRTUAL TABLE messages_fts USING fts5(
    message,
    datetime UNINDEXED,
    speaker UNINDEXED,
    account UNINDEXED,
    content='messages',
    content_rowid='id',
    tokenize='unicode61'
);
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Merged JSONL export")
    parser.add_argument("--output", required=True, type=Path, help="SQLite index path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        args.output.unlink()

    connection = sqlite3.connect(args.output)
    connection.executescript(SCHEMA)
    rows = []
    with args.input.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
            rows.append(
                (
                    int(item.get("timestamp") or 0),
                    str(item.get("datetime") or ""),
                    str(item.get("speaker") or "unknown"),
                    str(item.get("type") or "unknown"),
                    str(item.get("message") or ""),
                    str(item.get("account") or ""),
                    str(item.get("user_id") or ""),
                    str(item.get("server_id") or ""),
                    str(item.get("local_id") or ""),
                )
            )
            if len(rows) >= 2000:
                connection.executemany(
                    """INSERT INTO messages (
                        timestamp, datetime, speaker, type, message, account,
                        user_id, server_id, local_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    rows,
                )
                rows.clear()
    if rows:
        connection.executemany(
            """INSERT INTO messages (
                timestamp, datetime, speaker, type, message, account,
                user_id, server_id, local_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )
    connection.execute("INSERT INTO messages_fts(messages_fts) VALUES('rebuild')")
    connection.execute("CREATE INDEX messages_datetime_idx ON messages(datetime)")
    connection.execute("CREATE INDEX messages_speaker_idx ON messages(speaker)")
    connection.commit()
    count = connection.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    connection.close()
    print(f"Indexed {count} messages into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
