"""Quality checks for recipe CSV datasets."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


REQUIRED_COLUMNS = {
    "メニュー",
    "動画URL",
    "投稿者",
    "時間",
    "食材",
    "味",
    "油感",
    "詳細食材タグ",
    "ingredient_categories",
}

SUSPICIOUS_TAGS_BY_TITLE = {
    "スープ": {"rice", "udon", "soba", "pasta", "noodles", "rice_noodles"},
    "フレンチトースト": {"beef", "pork", "chicken", "fish", "rice"},
    "牛丼": {"aji", "yellowtail", "salmon", "mackerel", "rice_noodles"},
    "コーンスープ": {"beef", "pork", "chicken", "rice", "rice_noodles", "udon", "pasta"},
    "サラダ": {"rice", "udon", "soba", "pasta", "rice_noodles"},
}

TAG_TITLE_HINTS = {
    "rice": ("米", "ライス", "丼", "炒飯", "チャーハン", "オムライス", "おにぎり", "雑炊"),
    "udon": ("うどん",),
    "soba": ("そば", "蕎麦"),
    "pasta": ("パスタ", "スパゲッティ", "ナポリタン", "ペペロンチーノ", "カルボナーラ"),
    "noodles": ("中華麺", "焼きそば", "冷やし中華", "担々麺", "ラーメン"),
    "rice_noodles": ("ビーフン", "フォー"),
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as csv_file:
        return list(csv.DictReader(csv_file))


def split_tags(value: str) -> set[str]:
    return {item.strip() for item in (value or "").split(",") if item.strip()}


def check_required_columns(rows: list[dict[str, str]]) -> list[str]:
    if not rows:
        return ["CSV has no rows."]
    missing = REQUIRED_COLUMNS - set(rows[0].keys())
    return [f"Missing required columns: {', '.join(sorted(missing))}"] if missing else []


def check_duplicates(rows: list[dict[str, str]]) -> list[str]:
    warnings = []
    for column in ("video_id", "動画URL"):
        if column not in rows[0]:
            continue
        counts = Counter(row.get(column, "") for row in rows if row.get(column))
        duplicates = [value for value, count in counts.items() if count > 1]
        if duplicates:
            warnings.append(f"Duplicate {column}: {len(duplicates)} values")
    return warnings


def check_empty_fields(rows: list[dict[str, str]]) -> list[str]:
    warnings = []
    for index, row in enumerate(rows, 2):
        if not row.get("詳細食材タグ"):
            warnings.append(f"L{index} {row.get('メニュー')}: empty 詳細食材タグ")
        if not row.get("ingredient_categories"):
            warnings.append(f"L{index} {row.get('メニュー')}: empty ingredient_categories")
        if row.get("video_id") == "":
            warnings.append(f"L{index} {row.get('メニュー')}: empty video_id")
    return warnings


def check_suspicious_tags(rows: list[dict[str, str]]) -> list[str]:
    warnings = []
    for index, row in enumerate(rows, 2):
        title = row.get("メニュー") or ""
        tags = split_tags(row.get("詳細食材タグ") or "")
        for title_word, suspicious_tags in SUSPICIOUS_TAGS_BY_TITLE.items():
            if title_word not in title:
                continue
            found = {
                tag
                for tag in tags & suspicious_tags
                if not any(hint in title for hint in TAG_TITLE_HINTS.get(tag, ()))
            }
            if found:
                warnings.append(f"L{index} {title}: suspicious tags {', '.join(sorted(found))}")
    return warnings


def check_distribution(rows: list[dict[str, str]]) -> list[str]:
    warnings = []
    category_counts = Counter()
    for row in rows:
        category_counts.update(
            item for item in (row.get("ingredient_categories") or "").split(";") if item
        )
    if category_counts:
        most_common_category, count = category_counts.most_common(1)[0]
        if count / len(rows) > 0.85:
            warnings.append(
                f"Category distribution may be biased: {most_common_category} appears in {count}/{len(rows)} rows"
            )
    return warnings


def run_checks(path: Path) -> list[str]:
    rows = read_rows(path)
    warnings = []
    warnings.extend(check_required_columns(rows))
    if rows:
        warnings.extend(check_duplicates(rows))
        warnings.extend(check_empty_fields(rows))
        warnings.extend(check_suspicious_tags(rows))
        warnings.extend(check_distribution(rows))
    return warnings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check recipe dataset quality.")
    parser.add_argument("csv_path")
    parser.add_argument("--fail-on-warning", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    warnings = run_checks(Path(args.csv_path))
    if not warnings:
        print("OK: no quality warnings")
        return

    print(f"Quality warnings: {len(warnings)}")
    for warning in warnings[:200]:
        print(f"- {warning}")
    if len(warnings) > 200:
        print(f"... and {len(warnings) - 200} more")
    if args.fail_on_warning:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
