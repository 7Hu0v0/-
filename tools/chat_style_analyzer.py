#!/usr/bin/env python3
"""Summarize linguistic patterns from a JSONL chat export."""

from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import Counter
from pathlib import Path


KEYWORDS = [
    "老公",
    "宝宝",
    "宝贝",
    "想你",
    "喜欢你",
    "爱你",
    "对不起",
    "没事",
    "算了",
    "随便",
    "无语",
    "烦",
    "困",
    "睡",
    "分手",
    "复合",
    "拉黑",
    "游戏",
    "别问",
    "不知道",
    "不想",
    "不要",
    "滚",
    "哈哈",
    "呜呜",
    "。。",
    "……",
]


def load_target_text(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as source:
        for line in source:
            record = json.loads(line)
            if record.get("speaker") != "target" or record.get("type_id") != 1:
                continue
            message = record.get("message", "").strip()
            if not message or message.startswith("<msg") or message.startswith("<?xml"):
                continue
            record["message"] = re.sub(r"\s+", " ", message)
            records.append(record)
    return records


def safe_sample(records: list[dict], keyword: str, limit: int = 8) -> list[dict]:
    matches = [record for record in records if keyword in record["message"]]
    if len(matches) <= limit:
        return matches
    step = max(1, len(matches) // limit)
    return matches[::step][:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze target-speaker chat style")
    parser.add_argument("jsonl")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    records = load_target_text(Path(args.jsonl))
    messages = [record["message"] for record in records]
    lengths = [len(message) for message in messages]
    exact = Counter(messages)
    accounts = Counter(record["account"] for record in records)
    hours = Counter(int(record["datetime"][11:13]) for record in records)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as report:
        report.write("# Chat Style Evidence\n\n")
        report.write(f"- Target text messages: {len(records)}\n")
        report.write(f"- Mean length: {statistics.mean(lengths):.2f}\n")
        report.write(f"- Median length: {statistics.median(lengths):.0f}\n")
        report.write(f"- Messages <= 2 chars: {sum(length <= 2 for length in lengths)}\n")
        report.write(f"- Messages <= 5 chars: {sum(length <= 5 for length in lengths)}\n")
        report.write(f"- Accounts: {dict(accounts)}\n\n")

        report.write("## Punctuation\n\n")
        for token in ["。", "。。", "...", "！", "!", "？", "?", "～", "~"]:
            report.write(f"- `{token}`: {sum(message.count(token) for message in messages)}\n")

        report.write("\n## Active Hours\n\n")
        for hour, count in hours.most_common():
            report.write(f"- {hour:02d}:00: {count}\n")

        report.write("\n## Frequent Exact Messages\n\n")
        for message, count in exact.most_common(80):
            if len(message) > 80:
                continue
            report.write(f"- {count}x: {message}\n")

        report.write("\n## Keyword Counts And Samples\n")
        for keyword in KEYWORDS:
            matches = [record for record in records if keyword in record["message"]]
            report.write(f"\n### {keyword}: {len(matches)}\n\n")
            for record in safe_sample(records, keyword):
                message = record["message"][:180]
                report.write(
                    f"- {record['datetime']} [{record['account']}]: {message}\n"
                )

    print(f"Analyzed {len(records)} target text messages")
    print(output)


if __name__ == "__main__":
    main()
