"""Create a stratified recipe audit CSV for manual review."""

from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict
from pathlib import Path


AUDIT_COLUMNS = [
    "video_id",
    "title",
    "video_url",
    "creator",
    "current_ingredients",
    "current_tags",
    "current_time",
    "current_temperature",
    "current_knife",
    "current_heat",
    "audit_category",
    "correct_ingredients",
    "correct_time",
    "correct_temperature",
    "correct_knife",
    "correct_heat",
    "reviewer",
    "reviewed_at",
    "review_status",
    "notes",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as csv_file:
        return list(csv.DictReader(csv_file))


def categories(row: dict[str, str]) -> list[str]:
    return [item for item in (row.get("ingredient_categories") or "").split(";") if item]


def build_sample(rows: list[dict[str, str]], target_count: int, seed: int) -> list[dict[str, str]]:
    random.seed(seed)
    buckets: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        row_categories = categories(row) or ["未分類"]
        for category in row_categories:
            buckets[category].append(row)

    for bucket_rows in buckets.values():
        random.shuffle(bucket_rows)

    selected = []
    seen_ids = set()
    category_names = sorted(buckets)
    while len(selected) < target_count:
        added = False
        for category in category_names:
            while buckets[category]:
                row = buckets[category].pop()
                video_id = row.get("video_id") or row.get("external_id") or row.get("動画URL")
                if video_id in seen_ids:
                    continue
                seen_ids.add(video_id)
                selected.append((row, category))
                added = True
                break
            if len(selected) >= target_count:
                break
        if not added:
            break
    return [to_audit_row(row, category) for row, category in selected]


def to_audit_row(row: dict[str, str], category: str) -> dict[str, str]:
    return {
        "video_id": row.get("video_id", ""),
        "title": row.get("メニュー", ""),
        "video_url": row.get("video_url") or row.get("動画URL", ""),
        "creator": row.get("投稿者", ""),
        "current_ingredients": row.get("食材", ""),
        "current_tags": row.get("詳細食材タグ", ""),
        "current_time": row.get("時間", ""),
        "current_temperature": row.get("temperature", ""),
        "current_knife": row.get("knife", ""),
        "current_heat": row.get("heat", ""),
        "audit_category": category,
        "correct_ingredients": "",
        "correct_time": "",
        "correct_temperature": "",
        "correct_knife": "",
        "correct_heat": "",
        "reviewer": "",
        "reviewed_at": "",
        "review_status": "unreviewed",
        "notes": "",
    }


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=AUDIT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a stratified manual audit sample.")
    parser.add_argument("--input", default="data/1000件料理レシピ.csv")
    parser.add_argument("--output", default="data/recipe-audit-sample.csv")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260823)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = build_sample(read_rows(Path(args.input)), args.count, args.seed)
    write_rows(Path(args.output), rows)
    print(f"Wrote {len(rows)} audit rows to {args.output}")


if __name__ == "__main__":
    main()
