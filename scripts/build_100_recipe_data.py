import csv
import json
import re
from pathlib import Path


SOURCE_CSV = Path("/Users/hanashirokeita/Desktop/大学/研究/30件料理レシピ.csv")
DETAILS_JSON = Path("data/youtube_details.json")
OUTPUT_JS = Path("recipes-data.js")
OUTPUT_CSV = Path("data/100件料理レシピ.csv")


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
    "oyster": "かき",
    "crab": "かに",
    "salmon": "サケ",
    "mackerel": "サバ",
    "saury": "サンマ",
    "shirasu": "しらす",
    "whitefish": "白身魚",
    "octopus": "たこ",
    "yellowtail": "ブリ",
    "scallop": "ほたて",
    "tuna_sashimi": "マグロ",
    "cabbage": "キャベツ",
    "cucumber": "きゅうり",
    "burdock": "ごぼう",
    "potato": "じゃが芋",
    "daikon": "大根",
    "onion": "玉ねぎ",
    "tomato": "トマト",
    "eggplant": "なす",
    "nira": "にら",
    "carrot": "にんじん",
    "green_onion": "ネギ",
    "bell_pepper": "ピーマン",
    "broccoli": "ブロッコリー",
    "spinach": "ほうれん草",
    "bean_sprouts": "もやし",
    "lotus_root": "レンコン",
    "pumpkin": "かぼちゃ",
    "green_bean": "さやいんげん",
    "lettuce": "レタス",
    "egg": "卵",
    "tofu": "豆腐",
    "atsuage": "厚揚げ",
    "aburaage": "油揚げ",
    "wakame": "わかめ",
    "kombu": "昆布",
    "chikuwa": "ちくわ",
    "canned_tuna": "ツナ",
    "mentaiko": "明太子",
    "harusame": "春雨",
    "ginger": "ショウガ",
    "garlic": "にんにく",
    "konnyaku": "こんにゃく",
    "rice": "ご飯・米",
    "udon": "うどん",
    "soba": "そば",
    "noodles": "中華麺",
    "somen": "そうめん",
    "ramen": "ラーメン",
    "yakisoba_noodles": "焼きそば麺",
    "rice_noodles": "ビーフン・フォー",
    "pasta": "パスタ",
    "cheese": "チーズ",
    "butter": "バター",
    "curry_roux": "カレールゥ",
}

TAG_KEYWORDS = [
    ("beef", ["牛", "ビーフ", "ローストビーフ"]),
    ("pork", ["豚", "ポーク", "カツ", "回鍋肉", "酢豚", "豚汁"]),
    ("chicken", ["鶏", "チキン", "唐揚げ", "手羽", "油淋鶏"]),
    ("minced_meat", ["ひき肉", "挽き肉", "ミンチ", "ハンバーグ", "キーマ", "ミートソース", "肉詰め"]),
    ("bacon", ["ベーコン", "カルボナーラ"]),
    ("ham", ["ハム"]),
    ("salmon", ["鮭", "サーモン"]),
    ("yellowtail", ["ぶり", "ブリ"]),
    ("mackerel", ["さば", "サバ"]),
    ("aji", ["アジ", "あじの", "あじを"]),
    ("shrimp", ["エビ", "えび", "海老"]),
    ("shellfish", ["あさり", "クラム", "貝", "ボンゴレ"]),
    ("octopus", ["たこ", "タコ"]),
    ("tuna_sashimi", ["まぐろ", "マグロ"]),
    ("canned_tuna", ["ツナ"]),
    ("rice", ["ご飯", "ごはん", "丼", "飯", "ライス", "米", "オムライス", "チャーハン"]),
    ("egg", ["卵", "玉子", "たまご", "オム", "天津飯", "茶碗蒸し"]),
    ("tofu", ["豆腐", "冷奴"]),
    ("aburaage", ["きつねうどん", "油揚げ", "お揚げ"]),
    ("pasta", ["パスタ", "スパゲッティ", "ナポリタン", "ペペロンチーノ", "ボンゴレ"]),
    ("udon", ["うどん"]),
    ("soba", ["そば"]),
    ("noodles", ["中華麺", "冷やし中華", "焼きそば", "担々麺"]),
    ("yakisoba_noodles", ["焼きそば"]),
    ("somen", ["そうめん"]),
    ("ramen", ["ラーメン", "担々麺"]),
    ("rice_noodles", ["フォー", "ビーフン"]),
    ("harusame", ["春雨"]),
    ("cabbage", ["キャベツ", "コールスロー", "回鍋肉", "ロールキャベツ", "お好み焼き"]),
    ("cucumber", ["きゅうり", "冷やし中華"]),
    ("burdock", ["ごぼう", "きんぴら"]),
    ("potato", ["じゃが", "ポテト", "コロッケ"]),
    ("onion", ["玉ねぎ", "オニオン"]),
    ("carrot", ["にんじん", "人参"]),
    ("tomato", ["トマト", "カプレーゼ", "ラタトゥイユ", "ミネストローネ"]),
    ("eggplant", ["なす", "ナス", "ラタトゥイユ"]),
    ("bell_pepper", ["ピーマン", "ガパオ", "チンジャオ"]),
    ("green_onion", ["ねぎ", "ネギ", "長ネギ", "にら玉"]),
    ("nira", ["にら", "ニラ"]),
    ("spinach", ["ほうれん草"]),
    ("bean_sprouts", ["もやし"]),
    ("pumpkin", ["かぼちゃ"]),
    ("lotus_root", ["れんこん", "レンコン", "筑前煮"]),
    ("green_bean", ["いんげん"]),
    ("broccoli", ["ブロッコリー"]),
    ("wakame", ["わかめ"]),
    ("kombu", ["昆布", "塩昆布"]),
    ("garlic", ["にんにく", "ガーリック", "ペペロンチーノ"]),
    ("ginger", ["しょうが", "生姜"]),
    ("cheese", ["チーズ", "グラタン", "カプレーゼ", "ドリア"]),
    ("butter", ["バター", "ムニエル"]),
    ("curry_roux", ["カレー"]),
    ("mentaiko", ["明太子"]),
    ("chikuwa", ["ちくわ"]),
]

EXTRA_HINTS = {
    "牛丼": ["beef", "onion", "rice"],
    "豚丼": ["pork", "onion", "rice"],
    "カツ丼": ["pork", "egg", "onion", "rice"],
    "タコライス": ["minced_meat", "lettuce", "tomato", "cheese", "rice"],
    "ビビンバ": ["beef", "bean_sprouts", "spinach", "rice"],
    "炊き込みご飯": ["rice", "chicken", "carrot"],
    "筑前煮": ["chicken", "carrot", "lotus_root", "konnyaku"],
    "魚の煮付け": ["whitefish", "ginger"],
    "ゴーヤチャンプルー": ["pork", "tofu", "egg"],
    "茶碗蒸し": ["egg", "chicken"],
    "卵サンド": ["egg"],
    "クラムチャウダー": ["shellfish", "potato", "onion"],
    "コーンスープ": ["onion"],
    "天ぷら": ["shrimp", "eggplant", "pumpkin"],
    "たこ焼き": ["octopus", "egg"],
    "フレンチトースト": ["egg", "butter"],
    "ホットサンド": ["cheese", "ham"],
    "カプレーゼ": ["tomato", "cheese"],
    "サバ缶サラダ": ["mackerel", "cabbage"],
    "冷奴アレンジ": ["tofu", "green_onion", "ginger"],
}

MEAT_TAGS = {"beef", "pork", "chicken", "minced_meat", "ham", "bacon"}
FISH_TAGS = {"aji", "squid", "sardine", "shrimp", "shellfish", "oyster", "crab", "salmon", "mackerel", "saury", "shirasu", "whitefish", "octopus", "yellowtail", "scallop", "tuna_sashimi", "canned_tuna"}
VEGETABLE_TAGS = {"cabbage", "cucumber", "burdock", "potato", "daikon", "onion", "tomato", "eggplant", "nira", "carrot", "green_onion", "bell_pepper", "broccoli", "spinach", "bean_sprouts", "lotus_root", "pumpkin", "green_bean", "lettuce"}
SOY_TAGS = {"tofu", "atsuage", "aburaage"}


def clean(value):
    return re.sub(r"\s+", " ", (value or "").strip())


def video_id(url):
    match = re.search(r"(?:shorts/|youtu\.be/|v=)([A-Za-z0-9_-]{11})", url or "")
    return match.group(1) if match else ""


def normalize_url(url):
    vid = video_id(url)
    return f"https://www.youtube.com/watch?v={vid}" if vid else url


def infer_tags(*texts):
    joined = "\n".join(texts)
    tags = []
    for tag, keywords in TAG_KEYWORDS:
        if any(keyword in joined for keyword in keywords):
            tags.append(tag)
    for dish, extra in EXTRA_HINTS.items():
        if dish in joined:
            tags.extend(extra)
    unique = []
    for tag in tags:
        if tag in LABELS and tag not in unique:
            unique.append(tag)
    if any(word in joined for word in ["焼きそば", "やきそば"]) and "soba" in unique:
        unique.remove("soba")
    if "中華あじ" in joined and "aji" in unique:
        unique.remove("aji")
    return unique


def broad_categories(tags):
    categories = []
    if any(tag in VEGETABLE_TAGS for tag in tags):
        categories.append("vegetable")
    if any(tag in MEAT_TAGS for tag in tags):
        categories.append("meat")
    if any(tag in FISH_TAGS for tag in tags):
        categories.append("fish")
    if any(tag in SOY_TAGS for tag in tags):
        categories.append("soy")
    if any(tag not in VEGETABLE_TAGS | MEAT_TAGS | FISH_TAGS | SOY_TAGS for tag in tags):
        categories.append("other")
    return categories or ["other"]


def infer_taste(title):
    rich_words = ["丼", "カレー", "唐揚げ", "揚げ", "チキン南蛮", "油淋鶏", "回鍋肉", "酢豚", "担々麺", "グラタン", "コロッケ", "たこ焼き", "お好み焼き", "チーズ", "キムチ", "ビーフシチュー"]
    light_words = ["サラダ", "和え", "冷奴", "カプレーゼ", "ざるそば", "わかめスープ", "茶碗蒸し", "煮物", "ごま和え", "ナムル", "ムニエル", "ホイル焼き"]
    if any(word in title for word in rich_words):
        return "rich"
    if any(word in title for word in light_words):
        return "light"
    if any(word in title for word in ["スープ", "ポトフ", "汁", "煮付け", "南蛮漬け"]):
        return "semi-light"
    return "semi-rich"


def infer_method(title, cooking_method=""):
    text = title + cooking_method
    if any(word in text for word in ["揚げ", "唐揚げ", "天ぷら", "コロッケ", "カツ"]):
        return "揚げる"
    if any(word in text for word in ["炒め", "焼きそば", "焼きうどん", "チャーハン", "チャンプルー", "ナポリタン", "回鍋肉", "豚キムチ"]):
        return "炒める"
    if any(word in text for word in ["焼き", "照り焼き", "ムニエル", "肉詰め", "お好み焼き", "たこ焼き", "ホイル焼き", "ホットサンド"]):
        return "焼く"
    if any(word in text for word in ["蒸し", "茶碗蒸し", "レンジ"]):
        return "蒸す"
    if any(word in text for word in ["パスタ", "うどん", "そば", "麺", "フォー", "そうめん"]):
        return "茹でる"
    if any(word in text for word in ["煮", "シチュー", "スープ", "汁", "カレー", "ポトフ", "チャウダー"]):
        return "煮る"
    if any(word in text for word in ["サラダ", "和え", "冷奴", "カプレーゼ", "漬け丼"]):
        return "和える"
    return "調理"


def infer_time(title):
    if any(word in title for word in ["ロールキャベツ", "ビーフシチュー", "ローストビーフ", "筑前煮", "コロッケ", "天ぷら", "たこ焼き", "グラタン"]):
        return "slow"
    if any(word in title for word in ["サラダ", "和え", "冷奴", "カプレーゼ", "卵サンド", "丼", "ナムル", "ごま和え", "スープ", "うどん", "そば", "そうめん"]):
        return "easy"
    return "normal"


def infer_temperature(title):
    if any(word in title for word in ["冷", "サラダ", "カプレーゼ", "ざるそば", "冷やし", "漬け丼"]):
        return "cold"
    return "warm"


def infer_load(title, method):
    effort = 2
    dishes = 2
    steps = 3
    if any(word in title for word in ["サラダ", "和え", "冷奴", "カプレーゼ", "丼", "スープ", "ナムル"]):
        effort, dishes, steps = 1, 1, 2
    if any(word in title for word in ["揚げ", "唐揚げ", "天ぷら", "コロッケ", "たこ焼き", "ロールキャベツ", "筑前煮"]):
        effort, dishes, steps = 4, 3, 5
    if any(word in title for word in ["シチュー", "グラタン", "茶碗蒸し", "ローストビーフ"]):
        effort, dishes, steps = 3, 3, 4
    oil = 2
    if method == "揚げる":
        oil = 5
    elif any(word in title for word in ["丼", "カレー", "炒め", "肉", "チーズ", "グラタン", "担々麺"]):
        oil = 4
    elif any(word in title for word in ["サラダ", "スープ", "煮物", "冷奴", "ざるそば"]):
        oil = 1
    return oil, effort, dishes, steps


def no_heat(title, method):
    return any(word in title for word in ["カプレーゼ", "きゅうり", "サバ缶サラダ", "冷奴", "漬け丼"]) or method == "和える"


def no_knife(tags, title):
    knife_needed_tags = VEGETABLE_TAGS | {"beef", "pork", "chicken", "yellowtail", "salmon", "mackerel"}
    if any(word in title for word in ["卵サンド", "そぼろ丼", "カルボナーラ", "和風パスタ"]):
        return True
    return not any(tag in knife_needed_tags for tag in tags)


def build_record(title, url, creator, source_food, source_taste="", source_oil="", source_method="", source_feature="", description=""):
    tags = infer_tags(title, source_food, description[:1200])
    if not tags:
        tags = ["rice"] if any(word in title for word in ["丼", "飯", "ライス"]) else ["other"]
    method = infer_method(title, source_method)
    oil, effort, dishes, steps = infer_load(title, method)
    if str(source_oil).strip().isdigit():
        oil = max(1, min(5, int(str(source_oil).strip())))
    taste = infer_taste(title + source_taste)
    if "ガッツリ" in source_taste or "濃い" in source_taste:
        taste = "rich"
    elif "あっさり" in source_taste or "さっぱり" in source_taste:
        taste = "light"
    labels = [LABELS[tag] for tag in tags if tag in LABELS]
    raw = "、".join(labels[:10]) + "など"
    return {
        "title": clean(title),
        "url": normalize_url(url),
        "videoId": video_id(url),
        "creator": clean(creator),
        "style": clean(source_feature) or "実在YouTubeレシピ",
        "taste": taste,
        "time": infer_time(title),
        "temperature": infer_temperature(title),
        "ingredients": broad_categories(tags),
        "oil": oil,
        "effort": effort,
        "dishes": dishes,
        "steps": steps,
        "knife": not no_knife(tags, title),
        "heat": not no_heat(title, method),
        "detailedIngredients": tags,
        "rawIngredients": raw,
        "description": f"{clean(creator)}の実在動画。{raw}を使う「{clean(title)}」のレシピです。",
    }


def main():
    existing = list(csv.DictReader(SOURCE_CSV.open(encoding="utf-8-sig", newline="")))
    details = json.loads(DETAILS_JSON.read_text(encoding="utf-8"))

    records = []
    seen_ids = set()

    for row in existing:
        url = normalize_url(row["動画URL"])
        vid = video_id(url)
        if vid in seen_ids:
            continue
        seen_ids.add(vid)
        records.append(
            build_record(
                row["メニュー"],
                url,
                row["投稿者"],
                row["食材"],
                row["味（これをどう表現するか）"],
                row["油感（油の量）"],
                row.get("調理方法", ""),
                row["特徴"],
            )
        )

    for item in details:
        url = normalize_url(item["url"])
        vid = video_id(url)
        if vid in seen_ids:
            continue
        seen_ids.add(vid)
        records.append(
            build_record(
                item["target"],
                url,
                item.get("creator") or "",
                item.get("description") or "",
                "",
                "",
                "",
                "実在YouTube動画",
                item.get("description") or "",
            )
        )

    records = records[:100]
    assert len(records) == 100, f"Expected 100 records, got {len(records)}"
    assert len({video_id(record["url"]) for record in records}) == 100

    OUTPUT_JS.write_text(
        "const recipes = " + json.dumps(records, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "メニュー",
                "動画URL",
                "video_id",
                "投稿者",
                "時間",
                "食材",
                "味",
                "油感",
                "特徴",
                "詳細食材タグ",
            ],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "メニュー": record["title"],
                    "動画URL": record["url"],
                    "video_id": record["videoId"],
                    "投稿者": record["creator"],
                    "時間": record["time"],
                    "食材": record["rawIngredients"],
                    "味": record["taste"],
                    "油感": record["oil"],
                    "特徴": record["style"],
                    "詳細食材タグ": ",".join(record["detailedIngredients"]),
                }
            )

    print(f"Wrote {OUTPUT_JS} and {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
