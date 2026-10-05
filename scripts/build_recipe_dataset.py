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
from recipe_feature_tags import build_feature_tags


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
    ("chicken", ["鶏肉", "鶏もも", "鶏むね", "ささみ", "チキン", "手羽", "焼き鳥", "やきとり"]),
    ("minced_meat", ["ひき肉", "挽肉", "挽き肉", "ミンチ", "餃子"]),
    ("ham", ["ハム"]),
    ("bacon", ["ベーコン"]),
    ("salmon", ["鮭", "サーモン"]),
    ("mackerel", ["さば", "サバ", "鯖"]),
    ("yellowtail", ["ブリ", "鰤", "ぶり大根"]),
    ("whitefish", ["白身魚", "タラ", "鱈"]),
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

EXCLUDED_TITLE_WORDS = (
    "まとめ",
    "ランキング",
    "献立",
    "作り置き",
    "総集編",
    "ライブ",
    "切り抜き",
    "vlog",
    "Vlog",
    "ブイログ",
    "食べ歩き",
    "食レポ",
    "大食い",
    "爆食",
    "咀嚼音",
    "ASMR",
    "モッパン",
    "mukbang",
)
RECIPE_HINT_WORDS = (
    "レシピ",
    "作り方",
    "料理",
    "簡単",
    "材料",
    "分量",
    "調味料",
    "作る",
    "作れる",
    "cooking",
    "recipe",
    "#shorts",
    "#Shorts",
)
NON_RECIPE_TEXT_PATTERNS = (
    "食べてみた",
    "食べるだけ",
    "購入品",
    "開封",
    "ルーティン",
    "日常",
    "旅行",
    "外食",
    "店紹介",
    "お店紹介",
    "飲み歩き",
)
MAX_DURATION_SECONDS = 300
TITLE_ONLY_TAGS = {"rice", "soba", "bread"}
NEGATED_TAG_PATTERNS = {
    "egg": ("卵液不要", "卵不要", "卵なし", "卵不使用", "卵を使わない"),
}
RECIPE_SECTION_MARKERS = (
    "今回のレシピはこちら",
    "今回のレシピ",
    "材料はこちら",
    "材料",
    "レシピはこちら",
)
PROMO_SECTION_MARKERS = (
    "◆",
    "▼",
    "～～",
    "書籍のお知らせ",
    "チャンネル登録",
    "こちらもおすすめ",
    "関連動画",
    "おすすめ動画",
    "SNS",
    "Twitter",
    "Instagram",
    "TikTok",
    "Amazon",
    "楽天",
    "ホームページ",
    "グッズ販売",
    "STORE",
    "ダウンロードはこちら",
    "お仕事",
    "サブチャンネル",
)


def clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def is_likely_recipe_record(title: str, description: str) -> bool:
    text = f"{title}\n{description[:1200]}"
    if any(word in text for word in NON_RECIPE_TEXT_PATTERNS):
        return False
    return any(word in text for word in RECIPE_HINT_WORDS)


def duration_seconds(record: dict) -> int:
    try:
        return int(float(record.get("duration_seconds") or 0))
    except (TypeError, ValueError):
        return 0


def trim_description_for_ingredient_extraction(description: str) -> str:
    """Keep likely recipe text and drop links, promos, SNS, and book sections."""
    if not description:
        return ""

    source = description
    using_recipe_section = False
    for marker in RECIPE_SECTION_MARKERS:
        marker_index = source.find(marker)
        if marker_index >= 0:
            source = source[marker_index:]
            using_recipe_section = True
            break

    promo_markers = PROMO_SECTION_MARKERS if using_recipe_section else tuple(
        marker for marker in PROMO_SECTION_MARKERS if marker not in {"◆", "▼", "～～"}
    )
    lines = []
    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(("http://", "https://")):
            continue
        if any(marker in line for marker in promo_markers):
            if lines:
                break
            continue
        lines.append(line)

    return "\n".join(lines)


def extract_tags(*texts: str) -> list[str]:
    """Extract ingredient tags from title and description text."""
    title = texts[0] if texts else ""
    description = texts[1] if len(texts) > 1 else ""
    relevant_description = trim_description_for_ingredient_extraction(description)
    joined = "\n".join([title, relevant_description])

    def collect_tags(joined_text: str) -> list[str]:
        found_tags = []
        for tag, keywords in TAG_KEYWORDS:
            source = title if tag in TITLE_ONLY_TAGS else joined_text
            if any(keyword in source for keyword in keywords):
                found_tags.append(tag)
        return found_tags

    tags = collect_tags(joined)
    if not tags and relevant_description != description:
        joined = "\n".join([title, description])
        tags = collect_tags(joined)
    tags = [
        tag
        for tag in tags
        if not any(pattern in joined for pattern in NEGATED_TAG_PATTERNS.get(tag, ()))
    ]
    if "rice" in tags and "pasta" in tags and re.search(r"パスタに|パスタへ|パスタ化|パスタアレンジ|パスタにアレンジ", joined):
        tags = [tag for tag in tags if tag != "rice"]
    return list(dict.fromkeys(tags))


def parse_tags(value: str | None) -> list[str]:
    return [tag.strip() for tag in (value or "").split(",") if tag.strip()]


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


def infer_temperature(title: str, tags: list[str]) -> str:
    warm_priority_words = (
        "焼き",
        "焼く",
        "炒め",
        "煮",
        "揚げ",
        "蒸し",
        "丼",
        "どんぶり",
        "ご飯",
        "ごはん",
        "食パン",
        "トースト",
        "ホットサンド",
        "バーガー",
        "ピザ",
        "ホットドッグ",
        "スープ",
        "味噌汁",
        "みそ汁",
        "鍋",
        "シチュー",
    )
    cold_words = ("冷奴", "冷やし", "冷製", "サラダ", "カプレーゼ", "ざる", "和え", "ナムル", "漬物")
    if any(tag in tags for tag in ("rice", "bread")):
        return "warm"
    if any(word in title for word in warm_priority_words):
        return "warm"
    if any(word in title for word in cold_words):
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


EXCLUDED_REVIEW_STATUSES = {"exclude", "excluded", "non_recipe"}


def load_master_facts(path: Path | None) -> dict[str, dict[str, str]]:
    if not path or not path.exists():
        return {}

    with path.open(newline="", encoding="utf-8-sig") as csv_file:
        rows = list(csv.DictReader(csv_file))

    facts = {}
    for row in rows:
        video_id = clean(row.get("video_id"))
        review_status = clean(row.get("review_status"))
        if video_id and review_status in EXCLUDED_REVIEW_STATUSES:
            facts[video_id] = row
            continue
        if review_status != "confirmed":
            continue
        exact_ingredients = parse_tags(row.get("exact_ingredients"))
        has_condition_override = any(
            clean(row.get(key))
            for key in ("time", "temperature", "uses_knife", "uses_heat", "oil", "effort", "visual_knife")
        )
        if video_id and (exact_ingredients or has_condition_override):
            facts[video_id] = row
    return facts


def choose_value(override: dict[str, str] | None, key: str, fallback: str) -> str:
    if not override:
        return fallback
    return clean(override.get(key)) or fallback


def choose_bool(override: dict[str, str] | None, key: str, fallback: bool) -> bool:
    if not override:
        return fallback
    value = clean(override.get(key)).lower()
    if value == "true":
        return True
    if value == "false":
        return False
    return fallback


def build_rows(
    records: list[dict],
    limit: int | None = None,
    master_facts: dict[str, dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    rows = []
    seen_ids = set()
    source_records_by_id = {}
    master_facts = master_facts or {}
    for record in records:
        video_id = record.get("video_id") or ""
        title = clean(record.get("title"))
        description = clean(record.get("description"))
        if not video_id or not title or video_id in seen_ids:
            continue
        override = master_facts.get(video_id)
        if override and clean(override.get("review_status")) in EXCLUDED_REVIEW_STATUSES:
            continue
        if any(word in title for word in EXCLUDED_TITLE_WORDS):
            continue
        is_confirmed = bool(override and clean(override.get("review_status")) == "confirmed")
        if not is_confirmed and not is_likely_recipe_record(title, description):
            continue
        record_duration_seconds = duration_seconds(record)
        if not is_confirmed and record_duration_seconds and record_duration_seconds > MAX_DURATION_SECONDS:
            continue

        tags = extract_tags(title, description)
        fact_status = "estimated"
        fact_source = "youtube_api_inferred"
        if override:
            override_tags = parse_tags(override.get("exact_ingredients"))
            if override_tags:
                tags = override_tags
                fact_status = "confirmed"
            fact_source = choose_value(override, "source", "manual")
        if not tags:
            continue

        seen_ids.add(video_id)
        source_records_by_id[video_id] = record
        categories = generate_ingredient_categories(",".join(tags))
        time_level = choose_value(override, "time", infer_time(title, description))
        temperature = choose_value(override, "temperature", infer_temperature(title, tags))
        oil = int(float(choose_value(override, "oil", str(infer_oil(title, tags)))))
        effort = int(float(choose_value(override, "effort", str(infer_effort(title, tags)))))
        dishes = infer_dishes(title, effort)
        knife = choose_bool(override, "visual_knife", choose_bool(override, "uses_knife", infer_knife(tags)))
        heat = choose_bool(override, "uses_heat", infer_heat(title, temperature))

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
                "knife": str(knife).lower(),
                "heat": str(heat).lower(),
                "thumbnail_url": clean(record.get("thumbnail_url")),
                "fact_status": fact_status,
                "fact_source": fact_source,
            }
        )
        if limit and len(rows) >= limit:
            break

    scored_rows = add_richness_and_taste_level_to_rows(rows)
    for row in scored_rows:
        row["味"] = infer_taste_from_level(row.get("taste_level", ""))
        row.update(
            build_feature_tags(
                row,
                source_records_by_id.get(row.get("video_id", "")),
                master_facts.get(row.get("video_id", "")),
            )
        )
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


def write_review_csv(path: Path, rows: list[dict[str, str]]) -> None:
    review_rows = [row for row in rows if row.get("tag_review_status") == "needs_review"]
    if not review_rows:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
        return
    columns = [
        "video_id",
        "メニュー",
        "動画URL",
        "投稿者",
        "tag_review_reasons",
        "genre",
        "genre_confidence",
        "genre_basis",
        "staple",
        "staple_confidence",
        "staple_basis",
        "dish_shape",
        "dish_shape_confidence",
        "dish_shape_basis",
        "main_ingredient",
        "main_ingredient_confidence",
        "main_ingredient_basis",
        "temperature_tag",
        "temperature_tag_confidence",
        "temperature_tag_basis",
        "time_tag",
        "time_tag_confidence",
        "time_tag_basis",
        "uses_knife_tag",
        "uses_knife_tag_confidence",
        "uses_knife_tag_basis",
        "uses_heat_tag",
        "uses_heat_tag_confidence",
        "uses_heat_tag_basis",
        "uses_frying_pan",
        "uses_frying_pan_confidence",
        "uses_frying_pan_basis",
        "uses_microwave",
        "uses_microwave_confidence",
        "uses_microwave_basis",
        "詳細食材タグ",
        "fact_status",
        "fact_source",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns)
        writer.writeheader()
        writer.writerows({column: row.get(column, "") for column in columns} for row in review_rows)


def to_bool(value: str) -> bool:
    return str(value).lower() == "true"


def to_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


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
                "ingredientStatus": row.get("fact_status", "estimated"),
                "ingredientSource": row.get("fact_source", "youtube_api_inferred"),
                "featureTags": {
                    "genre": row.get("genre", ""),
                    "genreConfidence": to_float(row.get("genre_confidence", "")),
                    "staple": row.get("staple", ""),
                    "stapleConfidence": to_float(row.get("staple_confidence", "")),
                    "dishShape": row.get("dish_shape", ""),
                    "dishShapeConfidence": to_float(row.get("dish_shape_confidence", "")),
                    "mainIngredient": row.get("main_ingredient", ""),
                    "mainIngredientConfidence": to_float(row.get("main_ingredient_confidence", "")),
                    "taste": row.get("taste_tag", ""),
                    "tasteConfidence": to_float(row.get("taste_tag_confidence", "")),
                    "temperature": row.get("temperature_tag", ""),
                    "temperatureConfidence": to_float(row.get("temperature_tag_confidence", "")),
                    "time": row.get("time_tag", ""),
                    "timeConfidence": to_float(row.get("time_tag_confidence", "")),
                    "usesKnife": to_bool(row.get("uses_knife_tag", "")),
                    "usesKnifeConfidence": to_float(row.get("uses_knife_tag_confidence", "")),
                    "usesHeat": to_bool(row.get("uses_heat_tag", "")),
                    "usesHeatConfidence": to_float(row.get("uses_heat_tag_confidence", "")),
                    "usesFryingPan": to_bool(row.get("uses_frying_pan", "")),
                    "usesFryingPanConfidence": to_float(row.get("uses_frying_pan_confidence", "")),
                    "usesMicrowave": to_bool(row.get("uses_microwave", "")),
                    "usesMicrowaveConfidence": to_float(row.get("uses_microwave_confidence", "")),
                    "reviewStatus": row.get("tag_review_status", ""),
                    "reviewReasons": row.get("tag_review_reasons", ""),
                },
                "description": (
                    f"{row['投稿者']}の実在動画。{row['食材']}を使う「{row['メニュー']}」のレシピです。"
                    if row.get("fact_status") == "confirmed"
                    else f"{row['投稿者']}の実在動画。食材候補: {row['食材']}。「{row['メニュー']}」のレシピです。"
                ),
            }
        )
    path.write_text("const recipes = " + json.dumps(recipes, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build scored recipe dataset from YouTube records.")
    parser.add_argument("--input", default="data/youtube_api_recipes.json")
    parser.add_argument("--csv-output", default="data/1000件料理レシピ.csv")
    parser.add_argument("--json-output", default="data/1000_recipes_scored.json")
    parser.add_argument("--js-output", default="recipes-data.js")
    parser.add_argument("--master-data", default="data/recipes-master.csv")
    parser.add_argument("--review-output", default="data/recipe-tag-review.csv")
    parser.add_argument("--limit", type=int, default=1000)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    records = load_records(Path(args.input))
    rows = build_rows(records, args.limit, load_master_facts(Path(args.master_data)))
    if not rows:
        raise RuntimeError("No recipe rows were built.")
    write_csv(Path(args.csv_output), rows)
    write_json(Path(args.json_output), rows)
    write_review_csv(Path(args.review_output), rows)
    write_js(Path(args.js_output), rows)
    print(f"Built {len(rows)} recipes")


if __name__ == "__main__":
    main()
