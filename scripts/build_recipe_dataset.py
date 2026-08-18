"""Build scored recipe CSV/JS from collected YouTube records."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

from ingredient_score import (
    add_richness_and_taste_level_to_rows,
    generate_ingredient_categories,
)


LABELS = {
    "beef": "牛肉",
    "pork": "豚肉",
    "chicken": "鶏肉",
    "minced_meat": "挽肉",
    "ham": "ハム",
    "bacon": "ベーコン",
    "salmon": "サケ",
    "mackerel": "サバ",
    "yellowtail": "ブリ",
    "whitefish": "白身魚",
    "aji": "アジ",
    "shrimp": "えび",
    "shellfish": "貝",
    "octopus": "たこ",
    "tuna_sashimi": "マグロ",
    "canned_tuna": "ツナ",
    "tofu": "豆腐",
    "atsuage": "厚揚げ",
    "aburaage": "油揚げ",
    "egg": "卵",
    "rice": "ご飯・米",
    "udon": "うどん",
    "soba": "そば",
    "noodles": "中華麺",
    "somen": "そうめん",
    "ramen": "ラーメン",
    "rice_noodles": "ビーフン・フォー",
    "pasta": "パスタ",
    "harusame": "春雨",
    "cabbage": "キャベツ",
    "cucumber": "きゅうり",
    "spinach": "ほうれん草",
    "komatsuna": "小松菜",
    "nira": "にら",
    "green_onion": "ネギ",
    "bean_sprouts": "もやし",
    "lettuce": "レタス",
    "tomato": "トマト",
    "eggplant": "なす",
    "bell_pepper": "ピーマン",
    "broccoli": "ブロッコリー",
    "bitter_melon": "ゴーヤ",
    "potato": "じゃが芋",
    "onion": "玉ねぎ",
    "carrot": "にんじん",
    "daikon": "大根",
    "burdock": "ごぼう",
    "pumpkin": "かぼちゃ",
    "lotus_root": "レンコン",
    "corn": "コーン缶",
    "enoki": "えのき茸",
    "shimeji": "しめじ",
    "shiitake": "しいたけ",
    "wakame": "わかめ",
    "kombu": "昆布",
    "konnyaku": "こんにゃく",
    "ginger": "ショウガ",
    "garlic": "にんにく",
    "cheese": "チーズ",
    "butter": "バター",
    "mayonnaise": "マヨネーズ",
    "milk": "牛乳",
    "flour": "小麦粉",
    "bread": "パン",
    "curry_roux": "カレールゥ",
}

TAG_KEYWORDS = [
    ("beef", ["牛肉", "牛こま", "牛バラ", "ビーフ", "ローストビーフ"]),
    ("pork", ["豚肉", "豚バラ", "豚こま", "豚ロース", "ポーク"]),
    ("chicken", ["鶏肉", "鶏もも", "鶏むね", "ささみ", "チキン", "手羽"]),
    ("minced_meat", ["ひき肉", "挽肉", "挽き肉", "ミンチ", "餃子"]),
    ("ham", ["ハム"]),
    ("bacon", ["ベーコン"]),
    ("salmon", ["鮭", "サーモン"]),
    ("mackerel", ["さば", "サバ", "鯖"]),
    ("yellowtail", ["ブリ", "鰤", "ぶり大根"]),
    ("whitefish", ["白身魚", "たら", "鱈"]),
    ("aji", ["アジフライ", "アジの", "アジを", "鯵"]),
    ("shrimp", ["えび", "エビ", "海老"]),
    ("shellfish", ["あさり", "貝", "クラム", "ボンゴレ"]),
    ("octopus", ["たこ", "タコ"]),
    ("tuna_sashimi", ["まぐろ", "マグロ"]),
    ("canned_tuna", ["ツナ"]),
    ("tofu", ["豆腐", "冷奴"]),
    ("atsuage", ["厚揚げ"]),
    ("aburaage", ["油揚げ", "お揚げ"]),
    ("egg", ["卵", "たまご", "玉子"]),
    ("rice", ["米", "ライス", "丼", "炒飯", "チャーハン", "オムライス", "おにぎり", "雑炊"]),
    ("udon", ["うどん"]),
    ("soba", ["そば", "蕎麦"]),
    ("noodles", ["中華麺", "焼きそば", "冷やし中華", "担々麺"]),
    ("somen", ["そうめん"]),
    ("ramen", ["ラーメン"]),
    ("rice_noodles", ["フォー", "ビーフン"]),
    ("pasta", ["パスタ", "スパゲッティ", "ナポリタン", "ペペロンチーノ", "カルボナーラ"]),
    ("harusame", ["春雨"]),
    ("cabbage", ["キャベツ"]),
    ("napa_cabbage", ["白菜"]),
    ("cucumber", ["きゅうり", "キュウリ"]),
    ("spinach", ["ほうれん草"]),
    ("komatsuna", ["小松菜"]),
    ("nira", ["にら", "ニラ"]),
    ("green_onion", ["ねぎ", "ネギ", "長ネギ", "小ねぎ"]),
    ("bean_sprouts", ["もやし"]),
    ("lettuce", ["レタス"]),
    ("tomato", ["トマト"]),
    ("eggplant", ["なす", "ナス"]),
    ("bell_pepper", ["ピーマン"]),
    ("broccoli", ["ブロッコリー"]),
    ("bitter_melon", ["ゴーヤ"]),
    ("potato", ["じゃがいも", "じゃが芋", "ポテト"]),
    ("onion", ["玉ねぎ", "玉葱", "オニオン"]),
    ("carrot", ["にんじん", "人参"]),
    ("daikon", ["大根"]),
    ("burdock", ["ごぼう"]),
    ("pumpkin", ["かぼちゃ", "南瓜"]),
    ("lotus_root", ["れんこん", "レンコン"]),
    ("corn", ["コーン"]),
    ("enoki", ["えのき"]),
    ("shimeji", ["しめじ"]),
    ("shiitake", ["しいたけ", "椎茸"]),
    ("wakame", ["わかめ"]),
    ("kombu", ["昆布", "塩昆布"]),
    ("konnyaku", ["こんにゃく"]),
    ("ginger", ["しょうが", "生姜", "ショウガ"]),
    ("garlic", ["にんにく", "ニンニク", "ガーリック"]),
    ("cheese", ["チーズ"]),
    ("butter", ["バター"]),
    ("mayonnaise", ["マヨネーズ", "マヨ"]),
    ("milk", ["牛乳"]),
    ("flour", ["小麦粉", "薄力粉", "強力粉"]),
    ("bread", ["食パン", "パン粉", "トースト", "ホットサンド"]),
    ("curry_roux", ["カレールゥ", "カレールー", "カレー粉"]),
]

EXCLUDED_TITLE_WORDS = ("まとめ", "ランキング", "献立", "作り置き", "総集編", "ライブ", "切り抜き")
TITLE_ONLY_TAGS = {"rice", "soba", "bread"}


def clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def extract_tags(*texts: str) -> list[str]:
    """Extract ingredient tags from title and description text."""
    title = texts[0] if texts else ""
    joined = "\n".join(texts)
    tags = []
    for tag, keywords in TAG_KEYWORDS:
        source = title if tag in TITLE_ONLY_TAGS else joined
        if any(keyword in source for keyword in keywords):
            tags.append(tag)
    return list(dict.fromkeys(tags))


def infer_time(title: str, description: str) -> str:
    text = title + "\n" + description[:1000]
    match = re.search(r"(\d+)\s*分", text)
    if match:
        minutes = int(match.group(1))
        if minutes <= 15:
            return "easy"
        if minutes <= 30:
            return "normal"
        return "slow"
    if any(word in title for word in ("サラダ", "和え", "冷奴", "丼", "うどん", "そば")):
        return "easy"
    return "normal"


def infer_temperature(title: str) -> str:
    if any(word in title for word in ("冷", "サラダ", "カプレーゼ", "ざる", "冷やし", "漬け")):
        return "cold"
    return "warm"


def infer_oil(title: str, tags: list[str]) -> int:
    """Infer 1-5 oil level."""
    if any(word in title for word in ("揚げ", "唐揚げ", "天ぷら", "カツ", "フライ")):
        return 5
    if any(tag in tags for tag in ("butter", "cheese", "mayonnaise", "bacon")):
        return 4
    if any(word in title for word in ("炒め", "焼き", "チャーハン", "パスタ")):
        return 3
    if any(word in title for word in ("スープ", "煮", "蒸し", "茹で", "冷奴", "和え")):
        return 1
    return 2


def infer_effort(title: str, tags: list[str]) -> int:
    """Infer 1-5 cooking effort."""
    if any(word in title for word in ("ビーフシチュー", "ロールキャベツ", "筑前煮", "たこ焼き", "天ぷら")):
        return 5
    if len(tags) >= 7:
        return 4
    if any(word in title for word in ("丼", "和え", "冷奴", "サラダ", "スープ")):
        return 1
    return 3


def infer_dishes(title: str, effort: int) -> int:
    if any(word in title for word in ("丼", "和え", "冷奴", "サラダ")):
        return 1
    return 3 if effort >= 4 else 2


def infer_heat(title: str, temperature: str) -> bool:
    return not (temperature == "cold" and any(word in title for word in ("冷奴", "サラダ", "カプレーゼ", "和え")))


def infer_knife(tags: list[str]) -> bool:
    knife_tags = {
        "beef",
        "pork",
        "chicken",
        "cabbage",
        "onion",
        "carrot",
        "potato",
        "tomato",
        "eggplant",
        "cucumber",
        "green_onion",
    }
    return any(tag in knife_tags for tag in tags)


def infer_taste_from_level(taste_level: str) -> str:
    return {
        "あっさり": "light",
        "ややあっさり": "semi-light",
        "ややがっつり": "semi-rich",
        "がっつり": "rich",
    }.get(taste_level, "semi-rich")


def raw_ingredient_text(tags: list[str]) -> str:
    return "、".join(LABELS.get(tag, tag) for tag in tags)


def platform(record: dict) -> str:
    return clean(record.get("platform")) or "youtube"


def external_id(record: dict) -> str:
    return clean(record.get("external_id")) or clean(record.get("video_id"))


def video_url(record: dict) -> str:
    if record.get("video_url"):
        return record["video_url"]
    if record.get("url"):
        return record["url"]
    return f"https://www.youtube.com/watch?v={record.get('video_id', '')}"


def load_records(path: Path) -> list[dict]:
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    with path.open(newline="", encoding="utf-8-sig") as csv_file:
        return list(csv.DictReader(csv_file))


def build_rows(records: list[dict], limit: int | None = None) -> list[dict[str, str]]:
    rows = []
    seen_ids = set()
    for record in records:
        video_id = record.get("video_id") or ""
        title = clean(record.get("title"))
        description = clean(record.get("description"))
        if not video_id or not title or video_id in seen_ids:
            continue
        if any(word in title for word in EXCLUDED_TITLE_WORDS):
            continue

        tags = extract_tags(title, description)
        if not tags:
            continue

        seen_ids.add(video_id)
        categories = generate_ingredient_categories(",".join(tags))
        time_level = infer_time(title, description)
        temperature = infer_temperature(title)
        oil = infer_oil(title, tags)
        effort = infer_effort(title, tags)
        dishes = infer_dishes(title, effort)

        rows.append(
            {
                "メニュー": title,
                "platform": platform(record),
                "external_id": external_id(record),
                "video_url": video_url(record),
                "video_id": video_id,
                "動画URL": video_url(record),
                "投稿者": clean(record.get("channel") or record.get("creator")),
                "時間": time_level,
                "食材": raw_ingredient_text(tags),
                "味": "semi-rich",
                "油感": str(oil),
                "特徴": "YouTube Data API収集",
                "詳細食材タグ": ",".join(tags),
                "ingredient_categories": categories,
                "temperature": temperature,
                "effort": str(effort),
                "dishes": str(dishes),
                "knife": str(infer_knife(tags)).lower(),
                "heat": str(infer_heat(title, temperature)).lower(),
                "thumbnail_url": clean(record.get("thumbnail_url")),
            }
        )
        if limit and len(rows) >= limit:
            break

    scored_rows = add_richness_and_taste_level_to_rows(rows)
    for row in scored_rows:
        row["味"] = infer_taste_from_level(row.get("taste_level", ""))
    return scored_rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def to_bool(value: str) -> bool:
    return str(value).lower() == "true"


def write_js(path: Path, rows: list[dict[str, str]]) -> None:
    recipes = []
    for row in rows:
        recipes.append(
            {
                "title": row["メニュー"],
                "platform": row.get("platform", "youtube"),
                "externalId": row.get("external_id", row["video_id"]),
                "videoUrl": row.get("video_url", row["動画URL"]),
                "videoId": row["video_id"],
                "url": row["動画URL"],
                "thumbnailUrl": row.get("thumbnail_url", ""),
                "creator": row["投稿者"],
                "style": row["特徴"],
                "taste": row["味"],
                "time": row["時間"],
                "temperature": row["temperature"],
                "ingredients": row["ingredient_categories"].split(";"),
                "oil": int(float(row["油感"])),
                "effort": int(float(row["effort"])),
                "dishes": int(float(row["dishes"])),
                "steps": max(2, int(float(row["effort"])) + 1),
                "knife": to_bool(row["knife"]),
                "heat": to_bool(row["heat"]),
                "detailedIngredients": [tag for tag in row["詳細食材タグ"].split(",") if tag],
                "rawIngredients": row["食材"],
                "description": f"{row['投稿者']}の実在動画。{row['食材']}を使う「{row['メニュー']}」のレシピです。",
            }
        )
    path.write_text("const recipes = " + json.dumps(recipes, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build scored recipe dataset from YouTube records.")
    parser.add_argument("--input", default="data/youtube_api_recipes.json")
    parser.add_argument("--csv-output", default="data/1000件料理レシピ.csv")
    parser.add_argument("--json-output", default="data/1000_recipes_scored.json")
    parser.add_argument("--js-output", default="recipes-data.js")
    parser.add_argument("--limit", type=int, default=1000)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    records = load_records(Path(args.input))
    rows = build_rows(records, args.limit)
    if not rows:
        raise RuntimeError("No recipe rows were built.")
    write_csv(Path(args.csv_output), rows)
    write_json(Path(args.json_output), rows)
    write_js(Path(args.js_output), rows)
    print(f"Built {len(rows)} recipes")


if __name__ == "__main__":
    main()
