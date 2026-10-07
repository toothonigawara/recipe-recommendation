"""Quality checks for recipe CSV datasets."""

from __future__ import annotations

import argparse
import csv
import re
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
    "pasta": ("パスタ", "スパゲッティ", "ナポリタン", "ペペロンチーノ", "カルボナーラ", "ミネストローネ"),
    "noodles": ("中華麺", "焼きそば", "冷やし中華", "担々麺", "ラーメン"),
    "rice_noodles": ("ビーフン", "フォー"),
}

P0_TITLE_TAG_CONFLICTS = [
    {
        "title_includes": ("卵液不要", "卵不要", "卵なし", "卵不使用", "卵を使わない"),
        "forbidden_tags": {"egg"},
        "message": "title says egg is not used but egg tag is present",
    },
    {
        "title_includes": ("親子丼",),
        "forbidden_tags": {"whitefish"},
        "message": "oyakodon should not include whitefish unless manually confirmed",
    },
    {
        "title_includes": ("パスタに",),
        "forbidden_tags": {"rice"},
        "message": "pasta-conversion title should not keep rice tag",
    },
    {
        "title_includes": ("したら", "やったら", "みたら", "だったら"),
        "forbidden_tags": {"whitefish"},
        "message": "Japanese connective ending should not be interpreted as cod",
    },
]

NON_RECIPE_TITLE_PATTERNS = [
    {
        "required": ("下準備",),
        "hints": ("裏技", "暮らしの知恵", "大損", "秘密"),
        "message": "title looks like a prep-tip video rather than a complete recipe",
    },
    {
        "required": ("2ch有益スレ",),
        "hints": (),
        "message": "title looks like a discussion-summary video rather than a recipe",
    },
    {
        "required": ("保存術",),
        "hints": (),
        "message": "title looks like a storage-tip video rather than a recipe",
    },
    {
        "required": ("家事ハック",),
        "hints": (),
        "message": "title looks like a life-hack video rather than a recipe",
    },
    {
        "required": ("暮らしの知恵",),
        "hints": (),
        "message": "title looks like a life-tip video rather than a recipe",
    },
    {
        "required": ("知らないと損",),
        "hints": ("裏技", "焼き方"),
        "message": "title looks like a tip or technique video rather than a complete recipe",
    },
    {
        "required": ("Vlog",),
        "hints": (),
        "message": "title looks like a vlog rather than a recipe",
    },
    {
        "required": ("食べてみた",),
        "hints": (),
        "message": "title looks like an eating-only video rather than a recipe",
    },
    {
        "required": ("食レポ",),
        "hints": (),
        "message": "title looks like a food review rather than a recipe",
    },
    {
        "required": ("大食い",),
        "hints": (),
        "message": "title looks like an eating challenge rather than a recipe",
    },
    {
        "required": ("自炊記録",),
        "hints": (),
        "message": "title looks like a cooking diary rather than a single recipe",
    },
    {
        "required": ("ごはん記録",),
        "hints": (),
        "message": "title looks like a meal diary rather than a single recipe",
    },
    {
        "required": ("ご飯記録",),
        "hints": (),
        "message": "title looks like a meal diary rather than a single recipe",
    },
    {
        "required": ("お弁当記録",),
        "hints": (),
        "message": "title looks like a lunchbox diary rather than a single recipe",
    },
    {
        "required": ("保存法",),
        "hints": (),
        "message": "title looks like a storage-tip video rather than a recipe",
    },
]

NON_RECIPE_TITLE_REGEXES = [
    (re.compile(r"レシピ\s*[0-9０-９]+\s*選"), "title looks like a multi-recipe compilation"),
    (re.compile(r"[0-9０-９]+\s*選[】｜：:🍝]?"), "title looks like a list or compilation video"),
    (re.compile(r"[0-9０-９]+日間.*(?:自炊|ごはん|ご飯|弁当|節約)"), "title looks like a multi-day cooking diary"),
    (re.compile(r"(?:平日|休日)?[0-9０-９]+日(?:分|間).*?(?:ごはん|ご飯|弁当|自炊)"), "title looks like a multi-day cooking diary"),
    (re.compile(r"(?:週|週間).*?(?:ごはん|ご飯|自炊|弁当|献立|紹介)"), "title looks like a weekly meal diary or compilation"),
    (re.compile(r"(?:ごはん|ご飯|弁当|自炊).*?記録"), "title looks like a diary rather than a single recipe"),
    (re.compile(r"食費.*?(?:生活|記録|紹介|節約)"), "title looks like budget-life content rather than a single recipe"),
]
BENTO_SUBPOSITION_REGEX = re.compile(
    r"(?:お?弁当|べんとう|bento).{0,10}(?:にも|におすすめ|にもおすすめ|使える|ぴったり|便利)"
    r"|(?:お弁当|べんとう).{0,6}おかず"
)
BENTO_MAIN_REGEX = re.compile(
    r"(?:ランチケース|ランチボックス|lunchbox|lunch box)"
    r"|"
    r"(?:丼弁当|お?弁当レシピ|べんとうレシピ|bento recipe)"
    r"|"
    r"(?:お?弁当|べんとう|bento).{0,14}"
    r"(?:作り|づくり|詰め|詰め方|詰める|記録|献立|毎日|冷凍弁当|節約弁当|弁当レシピ|ランチケース|ランチボックス|lunchbox|lunch box)"
    r"|(?:旦那|夫|高校生|幼稚園|園児|息子|娘|OL|一人暮らし|同棲).{0,8}(?:お?弁当|べんとう)"
    r"|(?:お?弁当|べんとう|bento).{0,14}(?:旦那|夫|高校生|幼稚園|園児|息子|娘|OL|一人暮らし|同棲)"
    r"|(?:冷凍|節約|ズボラ|そうめん|パスタ|グラタン|カオマンガイ|うどん|ステーキ).{0,8}(?:お?弁当|べんとう)"
)


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


def check_p0_title_tag_conflicts(rows: list[dict[str, str]]) -> list[str]:
    warnings = []
    for index, row in enumerate(rows, 2):
        title = row.get("メニュー") or ""
        tags = split_tags(row.get("詳細食材タグ") or "")
        for rule in P0_TITLE_TAG_CONFLICTS:
            if not any(word in title for word in rule["title_includes"]):
                continue
            found = tags & rule["forbidden_tags"]
            if found:
                warnings.append(
                    f"P0 L{index} {title}: {rule['message']} ({', '.join(sorted(found))})"
                )
    return warnings


def check_non_recipe_titles(rows: list[dict[str, str]]) -> list[str]:
    warnings = []
    for index, row in enumerate(rows, 2):
        title = row.get("メニュー") or ""
        if BENTO_MAIN_REGEX.search(title) and not BENTO_SUBPOSITION_REGEX.search(title):
            warnings.append(f"P0 L{index} {title}: title looks like a lunchbox-making video")
        for rule in NON_RECIPE_TITLE_PATTERNS:
            has_required_words = all(word in title for word in rule["required"])
            has_hint_words = not rule["hints"] or any(word in title for word in rule["hints"])
            if has_required_words and has_hint_words:
                warnings.append(f"P0 L{index} {title}: {rule['message']}")
        for pattern, message in NON_RECIPE_TITLE_REGEXES:
            if pattern.search(title):
                warnings.append(f"P0 L{index} {title}: {message}")
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
        warnings.extend(check_p0_title_tag_conflicts(rows))
        warnings.extend(check_non_recipe_titles(rows))
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
