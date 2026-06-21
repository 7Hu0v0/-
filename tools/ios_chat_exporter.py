#!/usr/bin/env python3
"""Export and merge one-to-one chats from iOS WeChat SQLite databases."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path


MESSAGE_TYPES = {
    1: "text",
    3: "image",
    34: "voice",
    42: "contact_card",
    43: "video",
    47: "sticker",
    48: "location",
    49: "link_or_app",
    50: "call",
    62: "short_video",
    10000: "system",
}


def chat_table(user_id: str) -> str:
    digest = hashlib.md5(user_id.encode("utf-8")).hexdigest()
    return f"Chat_{digest}"


def normalize_message(message: object) -> str:
    if message is None:
        return ""
    if isinstance(message, bytes):
        return message.decode("utf-8", errors="replace")
    return str(message)


def read_source(db_path: Path, user_id: str, label: str) -> list[dict]:
    table = chat_table(user_id)
    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone()
        if not exists:
            raise ValueError(f"Chat table {table} not found in {db_path}")

        rows = connection.execute(
            f'SELECT CreateTime, Des, Type, Message, MesSvrID, MesLocalID FROM "{table}"'
        )
        records = []
        for created_at, des, msg_type, message, server_id, local_id in rows:
            records.append(
                {
                    "timestamp": int(created_at),
                    "datetime": datetime.fromtimestamp(int(created_at)).isoformat(
                        sep=" ", timespec="seconds"
                    ),
                    "speaker": "target" if des == 1 else "self",
                    "type": MESSAGE_TYPES.get(msg_type, f"type_{msg_type}"),
                    "type_id": int(msg_type),
                    "message": normalize_message(message),
                    "account": label,
                    "user_id": user_id,
                    "server_id": int(server_id or 0),
                    "local_id": int(local_id or 0),
                }
            )
        return records
    finally:
        connection.close()


def deduplicate(records: list[dict]) -> list[dict]:
    seen: set[tuple] = set()
    unique = []
    for record in sorted(records, key=lambda item: (item["timestamp"], item["local_id"])):
        if record["server_id"]:
            key = (record["server_id"], record["speaker"])
        else:
            key = (
                record["timestamp"],
                record["speaker"],
                record["type_id"],
                record["message"],
            )
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique


def write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_text(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as output:
        for record in records:
            message = record["message"].replace("\r", " ").replace("\n", " ").strip()
            if not message:
                message = f"[{record['type']}]"
            speaker = "她" if record["speaker"] == "target" else "我"
            output.write(
                f"{record['datetime']} | {speaker} | {record['account']} | {message}\n"
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export and merge iOS WeChat one-to-one chat tables"
    )
    parser.add_argument(
        "--source",
        action="append",
        nargs=3,
        metavar=("DB_PATH", "USER_ID", "LABEL"),
        required=True,
        help="Repeat for each account/database to merge",
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--basename", default="wechat_chat")
    args = parser.parse_args()

    records = []
    for db_path, user_id, label in args.source:
        records.extend(read_source(Path(db_path).expanduser(), user_id, label))
    records = deduplicate(records)

    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / f"{args.basename}.jsonl"
    text_path = output_dir / f"{args.basename}.txt"
    write_jsonl(jsonl_path, records)
    write_text(text_path, records)

    target_text = sum(
        record["speaker"] == "target" and record["type_id"] == 1 for record in records
    )
    print(f"Exported {len(records)} records ({target_text} target text messages)")
    print(jsonl_path)
    print(text_path)


if __name__ == "__main__":
    main()
