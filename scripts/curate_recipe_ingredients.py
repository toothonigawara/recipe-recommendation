"""Curate obvious ingredient tag errors in the 100 recipe dataset."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from ingredient_score import generate_ingredient_categories


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "100件料理レシピ.csv"
JS_PATH = ROOT / "recipes-data.js"


def extract_video_id(url: str) -> str:
    """YouTube URLから11桁のvideo_idを取り出す。"""
    match = re.search(r"(?:shorts/|youtu\.be/|v=)([A-Za-z0-9_-]{11})", url or "")
    return match.group(1) if match else ""


LABELS = {
    "beef": "牛肉",
    "pork": "豚肉",
    "chicken": "鶏肉",
    "minced_meat": "挽肉",
    "ham": "ハム",
    "bacon": "ベーコン",
    "aji": "アジ",
    "squid": "いか",
    "sardine": "イワシ",
    "shrimp": "えび",
    "shellfish": "貝",
    "salmon": "サケ",
    "mackerel": "サバ",
    "whitefish": "白身魚",
    "octopus": "たこ",
    "yellowtail": "ブリ",
    "tuna_sashimi": "マグロ",
    "canned_tuna": "ツナ",
    "cabbage": "キャベツ",
    "cucumber": "きゅうり",
    "green_bean": "さやいんげん",
    "komatsuna": "小松菜",
    "spinach": "ほうれん草",
    "bean_sprouts": "もやし",
    "lettuce": "レタス",
    "nira": "にら",
    "green_onion": "ネギ",
    "bok_choy": "チンゲン菜",
    "napa_cabbage": "白菜",
    "turnip": "かぶ",
    "pumpkin": "かぼちゃ",
    "burdock": "ごぼう",
    "sweet_potato": "さつま芋",
    "taro": "里芋",
    "potato": "じゃが芋",
    "daikon": "大根",
    "onion": "玉ねぎ",
    "nagaimo": "長芋",
    "carrot": "にんじん",
    "lotus_root": "レンコン",
    "tomato": "トマト",
    "eggplant": "なす",
    "bell_pepper": "ピーマン",
    "broccoli": "ブロッコリー",
    "bitter_melon": "ゴーヤ",
    "corn": "コーン缶",
    "enoki": "えのき茸",
    "shimeji": "しめじ",
    "shiitake": "しいたけ",
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
    "avocado": "アボカド",
    "curry_roux": "カレールゥ",
}


CURATED_TAGS = {
    "ねぎ塩豚チャーハン": ["pork", "rice", "egg", "green_onion", "garlic", "ginger"],
    "うどん": ["udon", "green_onion", "kombu"],
    "麻婆豆腐": ["minced_meat", "tofu", "green_onion", "garlic", "ginger"],
    "ハンバーグ": ["minced_meat", "egg", "onion"],
    "ガパオライス": ["minced_meat", "rice", "egg", "onion", "bell_pepper", "garlic"],
    "カルボナーラ": ["bacon", "egg", "pasta", "cheese"],
    "カレー": ["pork", "potato", "onion", "carrot", "curry_roux"],
    "肉じゃが": ["beef", "potato", "onion", "carrot", "green_bean"],
    "やきそば": ["pork", "noodles", "cabbage", "bean_sprouts"],
    "親子丼": ["chicken", "rice", "egg", "onion", "green_onion"],
    "にら玉": ["egg", "nira"],
    "餃子": ["minced_meat", "cabbage", "nira", "green_onion", "ginger", "garlic"],
    "チキンライス": ["chicken", "rice", "onion", "egg"],
    "ドリア": ["minced_meat", "rice", "onion", "cheese", "butter"],
    "角煮": ["pork", "egg", "ginger"],
    "そぼろ丼": ["minced_meat", "rice", "egg"],
    "チンジャオロース": ["pork", "bell_pepper"],
    "和風パスタ": ["canned_tuna", "pasta", "green_onion", "butter"],
    "ジャーマンポテト": ["bacon", "potato", "onion", "garlic"],
    "牛丼": ["beef", "rice", "onion", "ginger"],
    "豚丼": ["pork", "rice", "onion", "ginger"],
    "カツ丼": ["pork", "rice", "egg", "onion"],
    "天津飯": ["rice", "egg", "green_onion"],
    "オムライス": ["chicken", "rice", "egg", "onion", "butter"],
    "タコライス": ["minced_meat", "rice", "tomato", "lettuce", "cheese"],
    "ビビンバ": ["minced_meat", "rice", "egg", "carrot", "spinach", "bean_sprouts", "garlic"],
    "炊き込みご飯": ["chicken", "rice", "aburaage", "burdock", "carrot", "shiitake"],
    "ドライカレー": ["minced_meat", "rice", "onion", "carrot", "tomato", "bell_pepper", "curry_roux"],
    "キーマカレー": ["minced_meat", "rice", "onion", "tomato", "garlic", "ginger", "curry_roux"],
    "生姜焼き": ["pork", "onion", "ginger"],
    "豚キムチ": ["pork", "onion", "green_onion"],
    "回鍋肉": ["pork", "cabbage", "bell_pepper", "green_onion", "garlic"],
    "酢豚": ["pork", "egg", "carrot", "bell_pepper", "onion"],
    "鶏の照り焼き": ["chicken"],
    "唐揚げ": ["chicken", "ginger", "garlic"],
    "チキン南蛮": ["chicken", "egg", "onion"],
    "油淋鶏": ["chicken", "green_onion", "ginger"],
    "ロールキャベツ": ["minced_meat", "cabbage", "onion", "carrot"],
    "ビーフシチュー": ["beef", "onion", "carrot", "potato"],
    "クリームシチュー": ["chicken", "potato", "onion", "carrot", "broccoli", "milk", "butter"],
    "ローストビーフ": ["beef", "onion", "garlic"],
    "鶏むね肉のレンジ蒸し": ["chicken"],
    "手羽元のさっぱり煮": ["chicken", "egg", "broccoli", "garlic", "ginger"],
    "鮭のムニエル": ["salmon", "butter"],
    "鮭のホイル焼き": ["salmon", "onion", "shimeji", "butter"],
    "ぶりの照り焼き": ["yellowtail", "ginger"],
    "さばの味噌煮": ["mackerel", "ginger"],
    "あじの南蛮漬け": ["aji", "onion", "carrot", "bell_pepper"],
    "魚の煮付け": ["whitefish", "ginger"],
    "エビチリ": ["shrimp", "green_onion", "garlic", "ginger"],
    "アクアパッツァ": ["whitefish", "shellfish", "tomato", "garlic"],
    "ツナアボカド丼": ["canned_tuna", "rice", "avocado"],
    "まぐろ漬け丼": ["tuna_sashimi", "rice"],
    "ラタトゥイユ": ["bacon", "tomato", "eggplant", "bell_pepper", "onion"],
    "ミネストローネ": ["bacon", "cabbage", "potato", "tomato", "onion", "carrot"],
    "ポトフ": ["bacon", "cabbage", "potato", "onion", "carrot"],
    "ピーマンの肉詰め": ["minced_meat", "onion", "bell_pepper"],
    "なすの味噌炒め": ["eggplant", "green_onion", "ginger"],
    "かぼちゃの煮物": ["pumpkin"],
    "きんぴらごぼう": ["burdock", "carrot"],
    "ほうれん草のごま和え": ["spinach"],
    "もやしナムル": ["bean_sprouts"],
    "ポテトサラダ": ["ham", "egg", "cucumber", "potato", "onion", "mayonnaise"],
    "コールスロー": ["cabbage", "carrot", "mayonnaise"],
    "無限キャベツ": ["cabbage", "canned_tuna"],
    "筑前煮": ["chicken", "burdock", "carrot", "lotus_root", "konnyaku", "shiitake"],
    "揚げ出し豆腐": ["tofu", "green_onion", "ginger"],
    "豆腐ハンバーグ": ["minced_meat", "egg", "tofu", "onion"],
    "ゴーヤチャンプルー": ["pork", "egg", "tofu", "bitter_melon"],
    "だし巻き卵": ["egg"],
    "茶碗蒸し": ["chicken", "shrimp", "egg", "shiitake"],
    "卵サンド": ["egg", "bread", "mayonnaise"],
    "ナポリタン": ["pasta", "onion", "bell_pepper", "ham", "butter"],
    "ペペロンチーノ": ["pasta", "garlic"],
    "ミートソースパスタ": ["minced_meat", "pasta", "onion", "tomato", "cheese"],
    "ボンゴレ": ["shellfish", "pasta", "garlic", "butter"],
    "焼きうどん": ["pork", "udon", "cabbage", "green_onion"],
    "きつねうどん": ["aburaage", "udon", "green_onion"],
    "カレーうどん": ["pork", "udon", "onion", "green_onion", "curry_roux"],
    "ざるそば": ["soba", "green_onion"],
    "担々麺": ["minced_meat", "noodles", "green_onion"],
    "冷やし中華": ["chicken", "egg", "noodles", "cucumber", "ham", "tomato"],
    "そうめんチャンプルー": ["canned_tuna", "somen", "nira", "egg"],
    "フォー": ["chicken", "rice_noodles", "bean_sprouts"],
    "豚汁": ["pork", "carrot", "daikon", "green_onion", "burdock", "tofu"],
    "コーンスープ": ["corn", "onion", "flour", "milk", "butter"],
    "クラムチャウダー": ["shellfish", "bacon", "potato", "onion", "carrot", "milk", "butter"],
    "わかめスープ": ["wakame", "green_onion"],
    "オニオンスープ": ["onion", "butter"],
    "グラタン": ["chicken", "onion", "cheese", "butter", "milk", "flour"],
    "コロッケ": ["minced_meat", "egg", "potato", "onion"],
    "天ぷら": ["shrimp", "eggplant", "pumpkin", "egg", "flour"],
    "お好み焼き": ["pork", "egg", "cabbage", "flour"],
    "たこ焼き": ["octopus", "egg", "green_onion", "ginger", "flour"],
    "フレンチトースト": ["bread", "egg", "milk", "butter"],
    "ホットサンド": ["bread", "ham", "egg", "cheese", "butter"],
    "カプレーゼ": ["tomato", "cheese"],
    "きゅうりの塩昆布和え": ["cucumber", "kombu"],
    "サバ缶サラダ": ["mackerel", "cabbage", "onion", "carrot", "lettuce"],
    "冷奴アレンジ": ["tofu", "green_onion", "ginger"],
}


def raw_ingredient_text(tags: list[str]) -> str:
    return "、".join(LABELS.get(tag, tag) for tag in tags)


def recipe_categories(tags: list[str]) -> list[str]:
    categories = generate_ingredient_categories(",".join(tags))
    return [category for category in categories.split(";") if category]


def update_csv() -> None:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8-sig", newline="")))
    for row in rows:
        title = row["メニュー"]
        tags = CURATED_TAGS[title]
        row["video_id"] = extract_video_id(row.get("動画URL", ""))
        row["食材"] = raw_ingredient_text(tags)
        row["詳細食材タグ"] = ",".join(tags)
        row["ingredient_categories"] = generate_ingredient_categories(row["詳細食材タグ"])
        row.pop("調理方法", None)

    fieldnames = [fieldname for fieldname in rows[0].keys() if fieldname != "調理方法"]
    if "video_id" in fieldnames:
        fieldnames.remove("video_id")
    fieldnames.insert(fieldnames.index("動画URL") + 1, "video_id")
    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def update_js() -> None:
    text = JS_PATH.read_text(encoding="utf-8")
    prefix = "const recipes = "
    suffix = ";\n"
    records = json.loads(text.removeprefix(prefix).removesuffix(suffix))

    for record in records:
        title = record["title"]
        tags = CURATED_TAGS[title]
        raw = raw_ingredient_text(tags)
        record["videoId"] = extract_video_id(record.get("url", ""))
        record["detailedIngredients"] = tags
        record["rawIngredients"] = raw
        record["ingredients"] = recipe_categories(tags)
        record["description"] = f"{record['creator']}の実在動画。{raw}を使う「{title}」のレシピです。"
        record.pop("method", None)

    JS_PATH.write_text(
        prefix + json.dumps(records, ensure_ascii=False, indent=2) + suffix,
        encoding="utf-8",
    )


def main() -> None:
    missing = []
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8-sig", newline="")))
    for row in rows:
        if row["メニュー"] not in CURATED_TAGS:
            missing.append(row["メニュー"])
    if missing:
        raise ValueError(f"Missing curated tags: {missing}")

    update_csv()
    update_js()
    print(f"Curated {len(rows)} recipes")


if __name__ == "__main__":
    main()
