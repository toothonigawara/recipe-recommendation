"""Rule-based feature tagging for recipe recommendation data.

The recommender still uses the existing columns. These tags are extra metadata
for preference learning, audits, and future swipe-based personalization.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass


MEAT_TAGS = {"beef", "pork", "chicken", "minced_meat", "ham", "bacon"}
FISH_TAGS = {
    "salmon",
    "mackerel",
    "yellowtail",
    "whitefish",
    "aji",
    "shrimp",
    "shellfish",
    "octopus",
    "tuna_sashimi",
    "canned_tuna",
    "squid",
    "sardine",
    "saury",
    "shirasu",
    "oyster",
    "crab",
    "scallop",
    "mentaiko",
}
EGG_TAGS = {"egg"}
SOY_TAGS = {"tofu", "atsuage", "aburaage", "soybean", "natto", "okara"}
VEGETABLE_TAGS = {
    "cabbage",
    "napa_cabbage",
    "cucumber",
    "spinach",
    "komatsuna",
    "nira",
    "green_onion",
    "bean_sprouts",
    "lettuce",
    "tomato",
    "eggplant",
    "bell_pepper",
    "broccoli",
    "bitter_melon",
    "potato",
    "onion",
    "carrot",
    "daikon",
    "burdock",
    "pumpkin",
    "lotus_root",
    "corn",
    "enoki",
    "shimeji",
    "shiitake",
    "wakame",
    "kombu",
    "konnyaku",
    "asparagus",
    "avocado",
    "turnip",
    "sweet_potato",
    "taro",
    "green_bean",
    "shishito",
    "chrysanthemum",
    "celery",
    "bamboo_shoot",
    "bok_choy",
    "winter_melon",
    "nagaimo",
}
RICE_TAGS = {"rice"}
NOODLE_TAGS = {"udon", "soba", "noodles", "somen", "ramen", "yakisoba_noodles", "rice_noodles", "pasta", "harusame"}
BREAD_TAGS = {"bread", "flour"}

GENRE_RULES = (
    (
        "韓国",
        (
            "韓国",
            "キムチ",
            "ビビンバ",
            "チヂミ",
            "プルコギ",
            "ナムル",
            "スンドゥブ",
            "ユッケジャン",
            "コチュジャン",
            "ヤンニョム",
            "韓国風",
        ),
    ),
    (
        "中華",
        (
            "中華",
            "チャーハン",
            "炒飯",
            "餃子",
            "麻婆",
            "天津飯",
            "酢豚",
            "回鍋肉",
            "青椒肉絲",
            "担々",
            "ラーメン",
            "焼きそば",
            "中華麺",
        ),
    ),
    (
        "洋食",
        (
            "洋食",
            "パスタ",
            "スパゲッ",
            "ナポリタン",
            "カルボナーラ",
            "ペペロンチーノ",
            "グラタン",
            "ドリア",
            "オムライス",
            "ハンバーグ",
            "カレー",
            "シチュー",
            "ピザ",
            "トースト",
            "サンド",
            "バーガー",
            "リゾット",
            "ステーキ",
            "アヒージョ",
            "フレンチ",
        ),
    ),
    (
        "和食",
        (
            "和食",
            "和風",
            "照り焼き",
            "生姜焼き",
            "親子丼",
            "牛丼",
            "豚丼",
            "そぼろ丼",
            "カツ丼",
            "天丼",
            "丼",
            "味噌",
            "みそ",
            "醤油",
            "しょうゆ",
            "だし",
            "出汁",
            "肉じゃが",
            "肉豆腐",
            "冷奴",
            "炊き込み",
            "おにぎり",
            "寿司",
            "焼き鳥",
            "うどん",
            "そば",
            "蕎麦",
            "唐揚げ",
            "煮物",
            "japanesefood",
            "おうちごはん",
        ),
    ),
)

WARM_WORDS = ("焼き", "焼く", "炒め", "煮", "揚げ", "蒸し", "茹で", "丼", "ご飯", "ごはん", "スープ", "鍋", "シチュー")
COLD_WORDS = ("冷奴", "冷やし", "冷製", "サラダ", "カプレーゼ", "ざる", "和え", "ナムル", "漬物")
PAN_WORDS = ("フライパン", "ワンパン", "炒め", "焼き", "焼く", "焼くだけ")
MICROWAVE_WORDS = ("電子レンジ", "レンジ", "レンチン")


@dataclass(frozen=True)
class Decision:
    value: str
    confidence: float
    basis: str


def clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def parse_bool(value: str | None) -> bool | None:
    normalized = clean(value).lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    return None


def parse_tags(value: str | list[str] | None) -> list[str]:
    if isinstance(value, list):
        return [str(tag).strip() for tag in value if str(tag).strip()]
    return [tag.strip() for tag in (value or "").split(",") if tag.strip()]


def text_for_rules(title: str, description: str) -> str:
    return f"{title}\n{description[:1200]}"


def text_without_hashtags(title: str, description: str) -> str:
    title_core = re.split(r"[#＃]", title, maxsplit=1)[0]
    description_core = re.sub(r"[#＃]\S+", "", description[:1200])
    return f"{title_core}\n{description_core}"


def has_any_tag(tags: set[str], candidates: set[str]) -> bool:
    return bool(tags & candidates)


def first_matching_words(text: str, words: tuple[str, ...]) -> list[str]:
    return [word for word in words if word in text][:3]


def decide_genre(title: str, description: str, tags: set[str]) -> Decision:
    text = text_for_rules(title, description)
    matches = []
    for genre, words in GENRE_RULES:
        found = first_matching_words(text, words)
        if found:
            matches.append((genre, found))

    if matches:
        genre, found = matches[0]
        confidence = 0.95 if any(word in title for word in found) else 0.82
        if len(matches) > 1:
            confidence = min(confidence, 0.76)
        return Decision(genre, confidence, f"キーワード: {', '.join(found)}")

    if has_any_tag(tags, NOODLE_TAGS | RICE_TAGS | BREAD_TAGS | MEAT_TAGS | FISH_TAGS | EGG_TAGS | SOY_TAGS | VEGETABLE_TAGS):
        return Decision("その他", 0.72, "食材はあるがジャンル語がないためその他")
    return Decision("その他", 0.45, "ジャンル判定に使える語が少ない")


def decide_staple(title: str, description: str, tags: set[str]) -> Decision:
    text = text_without_hashtags(title, description)
    bread_text = re.sub(r"フライパン|ワンパン|パン粉", "", text)

    if "スープ" in title and not has_any_tag(tags, NOODLE_TAGS | RICE_TAGS | {"bread"}):
        return Decision("その他", 0.92, "スープ名で主食タグなし")
    if has_any_tag(tags, RICE_TAGS) and re.search(r"丼|どんぶり|丼ぶり|ご飯|ごはん|米", title):
        return Decision("ご飯", 0.94, "米タグとご飯料理名")
    if has_any_tag(tags, NOODLE_TAGS) or re.search(r"うどん|そば|蕎麦|パスタ|ラーメン|そうめん|素麺|焼きそば|ビーフン|フォー(?!ク)|春雨|麺", text):
        return Decision("麺", 0.95, "麺タグまたは麺料理名")
    if has_any_tag(tags, {"bread"}) or re.search(r"食パン|パン(?!粉|チ)|トースト|サンド|バーガー|ピザ|ホットドッグ", bread_text):
        return Decision("パン", 0.93, "パンタグまたはパン料理名")
    if "サラダ" in title and not has_any_tag(tags, RICE_TAGS):
        return Decision("その他", 0.90, "サラダ名で主食タグなし")
    if has_any_tag(tags, RICE_TAGS) or re.search(r"ご飯|ごはん|米|丼|炒飯|チャーハン|オムライス|雑炊|リゾット|おにぎり", text):
        return Decision("ご飯", 0.92, "米タグまたはご飯料理名")
    return Decision("その他", 0.82, "主食タグなし")


def decide_dish_shape(title: str, description: str, tags: set[str], staple: str) -> Decision:
    text = text_without_hashtags(title, description)
    bread_text = re.sub(r"フライパン|ワンパン|パン粉", "", text)

    if staple == "麺":
        return Decision("麺料理", 0.94, "主食タグが麺")
    if staple == "パン":
        return Decision("パン料理", 0.92, "主食タグがパン")
    if "スープ" in title and staple == "その他":
        return Decision("主菜", 0.80, "スープ名で主食料理ではない")
    if staple == "ご飯" and re.search(r"丼|どんぶり|丼ぶり|重|のっけご飯|乗っけご飯|ご飯に.+(?:のせ|乗せ|かけ)|ごはんに.+(?:のせ|乗せ|かけ)", text):
        return Decision("丼", 0.94, "丼・のっけご飯表現")
    if staple == "ご飯" and re.search(r"リゾット|雑炊|炒飯|チャーハン|オムライス|炊き込み|おにぎり|カレーライス|ドリア", text):
        return Decision("丼以外のご飯もの", 0.90, "丼以外の米料理名")
    if staple == "ご飯":
        return Decision("丼以外のご飯もの", 0.72, "米タグあり・丼表現なし")
    if re.search(r"煮込み|煮物|煮る|カレー|シチュー|ポトフ|肉じゃが", text):
        return Decision("煮込み", 0.88, "煮込み系キーワード")
    if re.search(r"食パン|パン(?!粉|チ)|トースト|サンド|バーガー|ピザ|ホットドッグ", bread_text):
        return Decision("パン料理", 0.90, "パン料理名")
    if has_any_tag(tags, MEAT_TAGS | FISH_TAGS | EGG_TAGS | SOY_TAGS | VEGETABLE_TAGS):
        return Decision("主菜", 0.78, "主材料タグあり・主食/煮込みではない")
    return Decision("その他", 0.58, "形の判定材料が少ない")


def decide_main_ingredient(title: str, description: str, tags: set[str]) -> Decision:
    text = text_for_rules(title, description)
    if "スープ" in title and not has_any_tag(tags, MEAT_TAGS | FISH_TAGS | EGG_TAGS | SOY_TAGS):
        if has_any_tag(tags, VEGETABLE_TAGS):
            return Decision("野菜中心", 0.78, f"スープの野菜タグ: {', '.join(sorted(tags & VEGETABLE_TAGS)[:4])}")
        return Decision("その他", 0.74, "スープ名で中心食材が弱い")
    if re.search(r"オムライス|チャーハン|炒飯|卵チャーハン|オムレツ|卵焼き|だし巻き", text):
        return Decision("卵", 0.92, "卵が主役になりやすい料理名")
    if has_any_tag(tags, MEAT_TAGS):
        return Decision("肉", 0.92, f"肉タグ: {', '.join(sorted(tags & MEAT_TAGS))}")
    if has_any_tag(tags, FISH_TAGS):
        return Decision("魚", 0.90, f"魚介タグ: {', '.join(sorted(tags & FISH_TAGS))}")
    if has_any_tag(tags, EGG_TAGS):
        return Decision("卵", 0.88, "卵タグ")
    if has_any_tag(tags, SOY_TAGS):
        return Decision("豆腐・大豆", 0.88, f"豆腐・大豆タグ: {', '.join(sorted(tags & SOY_TAGS))}")
    if has_any_tag(tags, VEGETABLE_TAGS):
        confidence = 0.86 if len(tags & VEGETABLE_TAGS) >= 2 else 0.74
        return Decision("野菜中心", confidence, f"野菜タグ: {', '.join(sorted(tags & VEGETABLE_TAGS)[:4])}")
    return Decision("その他", 0.66, "中心食材タグが弱い")


def decide_taste(row: dict[str, str], override: dict[str, str] | None) -> Decision:
    labels = {
        "rich": "ガッツリ",
        "semi-rich": "ややガッツリ",
        "semi-light": "ややあっさり",
        "light": "あっさり",
        "がっつり": "ガッツリ",
        "ややがっつり": "ややガッツリ",
        "ややあっさり": "ややあっさり",
        "あっさり": "あっさり",
    }
    if override and clean(override.get("richness")):
        richness = float(clean(override.get("richness")))
        if richness >= 7:
            value = "ガッツリ"
        elif richness >= 5:
            value = "ややガッツリ"
        elif richness >= 3:
            value = "ややあっさり"
        else:
            value = "あっさり"
        return Decision(value, 1.0, "recipes-master.csv のrichness")
    source = row.get("taste_level") or row.get("味") or ""
    value = labels.get(source, labels.get(clean(source), "ややガッツリ"))
    confidence = 0.82 if row.get("richness_score") else 0.70
    return Decision(value, confidence, f"richness_score={row.get('richness_score', '')}, 油感={row.get('油感', '')}")


def decide_temperature(title: str, description: str, tags: set[str], row: dict[str, str], override: dict[str, str] | None) -> Decision:
    if override and clean(override.get("temperature")):
        return Decision("温かい" if clean(override.get("temperature")) == "warm" else "冷たい", 1.0, "recipes-master.csv のtemperature")

    text = text_for_rules(title, description)
    if has_any_tag(tags, RICE_TAGS | {"bread"}):
        return Decision("温かい", 0.92, "ご飯・パン系は原則温かい")
    warm = first_matching_words(text, WARM_WORDS)
    cold = first_matching_words(text, COLD_WORDS)
    if warm and not cold:
        return Decision("温かい", 0.90, f"温かい調理語: {', '.join(warm)}")
    if cold and not warm:
        return Decision("冷たい", 0.88, f"冷たい料理語: {', '.join(cold)}")
    if row.get("temperature") == "cold":
        return Decision("冷たい", 0.72, "既存temperature列")
    return Decision("温かい", 0.72, "明確な温度語なし・既存推定")


def decide_time(title: str, description: str, row: dict[str, str], override: dict[str, str] | None) -> Decision:
    if override and clean(override.get("time")):
        mapping = {"easy": "15分以内", "normal": "15〜30分", "slow": "30分以上"}
        return Decision(mapping.get(clean(override.get("time")), clean(override.get("time"))), 1.0, "recipes-master.csv のtime")
    text = text_for_rules(title, description)
    match = re.search(r"(\d+)\s*分", text)
    if match:
        minutes = int(match.group(1))
        if minutes <= 15:
            return Decision("15分以内", 0.95, f"時間表現: {minutes}分")
        if minutes <= 30:
            return Decision("15〜30分", 0.95, f"時間表現: {minutes}分")
        return Decision("30分以上", 0.95, f"時間表現: {minutes}分")
    mapping = {"easy": "15分以内", "normal": "15〜30分", "slow": "30分以上"}
    return Decision(mapping.get(row.get("時間"), "15〜30分"), 0.72, "既存time列・明確な分数なし")


def decide_knife(title: str, description: str, tags: set[str], row: dict[str, str], override: dict[str, str] | None) -> Decision:
    if override:
        visual = parse_bool(override.get("visual_knife"))
        uses_knife = parse_bool(override.get("uses_knife"))
        if visual is not None:
            return Decision(bool_text(visual), 1.0, "recipes-master.csv のvisual_knife")
        if uses_knife is not None:
            return Decision(bool_text(uses_knife), 1.0, "recipes-master.csv のuses_knife")
    text = text_for_rules(title, description)
    if re.search(r"包丁(?:不要|なし|いらず|を使わない)|切らない|カット不要", text):
        return Decision("false", 0.95, "包丁不要表現")
    if re.search(r"切る|刻む|みじん切り|薄切り|千切り|一口大", text):
        return Decision("true", 0.88, "切る工程の表現")
    if row.get("knife") in {"true", "false"}:
        return Decision(row["knife"], 0.72, "既存knife列・食材推定")
    return Decision("false", 0.50, "包丁判定材料が少ない")


def decide_heat(title: str, description: str, row: dict[str, str], override: dict[str, str] | None) -> Decision:
    if override:
        uses_heat = parse_bool(override.get("uses_heat"))
        if uses_heat is not None:
            return Decision(bool_text(uses_heat), 1.0, "recipes-master.csv のuses_heat")
    text = text_for_rules(title, description)
    if re.search(r"火(?:を)?使わない|火なし|非加熱", text):
        return Decision("false", 0.95, "火を使わない表現")
    warm = first_matching_words(text, WARM_WORDS + PAN_WORDS)
    if warm:
        return Decision("true", 0.90, f"加熱調理語: {', '.join(warm)}")
    if any(word in text for word in MICROWAVE_WORDS):
        return Decision("true", 0.82, "電子レンジ加熱")
    if row.get("heat") in {"true", "false"}:
        return Decision(row["heat"], 0.70, "既存heat列")
    return Decision("true", 0.58, "加熱判定材料が少ない")


def decide_frying_pan(title: str, description: str, row: dict[str, str]) -> Decision:
    text = text_for_rules(title, description)
    found = first_matching_words(text, PAN_WORDS)
    if found:
        return Decision("true", 0.92, f"フライパン系表現: {', '.join(found)}")
    if any(word in text for word in ("オーブン", "トースター", "レンジ", "電子レンジ", "鍋")):
        return Decision("false", 0.76, "別調理器具の表現")
    if row.get("heat") == "false":
        return Decision("false", 0.78, "火を使わない既存判定")
    return Decision("false", 0.56, "フライパン表現なし")


def decide_microwave(title: str, description: str) -> Decision:
    text = text_for_rules(title, description)
    found = first_matching_words(text, MICROWAVE_WORDS)
    if found:
        return Decision("true", 0.95, f"電子レンジ表現: {', '.join(found)}")
    return Decision("false", 0.70, "電子レンジ表現なし")


def review_status(decisions: dict[str, Decision], master_confirmed: bool) -> tuple[str, list[str]]:
    if master_confirmed:
        return "confirmed", ["recipes-master.csvで確認済み"]

    thresholds = {
        "genre": 0.70,
        "staple": 0.70,
        "dish_shape": 0.70,
        "main_ingredient": 0.70,
        "temperature_tag": 0.70,
        "time_tag": 0.70,
        "uses_knife_tag": 0.65,
        "uses_heat_tag": 0.65,
        "uses_frying_pan": 0.55,
        "uses_microwave": 0.55,
    }
    reasons = [
        f"{key} confidence {decisions[key].confidence:.2f}"
        for key, threshold in thresholds.items()
        if key in decisions and decisions[key].confidence < threshold
    ]
    return ("needs_review", reasons) if reasons else ("auto_tagged", [])


def build_feature_tags(row: dict[str, str], source_record: dict | None = None, override: dict[str, str] | None = None) -> dict[str, str]:
    source_record = source_record or {}
    title = clean(row.get("メニュー") or source_record.get("title"))
    description = clean(source_record.get("description"))
    tags = set(parse_tags(row.get("詳細食材タグ")))
    master_confirmed = bool(override and clean(override.get("review_status")) == "confirmed")

    genre = decide_genre(title, description, tags)
    staple = decide_staple(title, description, tags)
    dish_shape = decide_dish_shape(title, description, tags, staple.value)
    main_ingredient = decide_main_ingredient(title, description, tags)
    taste = decide_taste(row, override)
    temperature = decide_temperature(title, description, tags, row, override)
    time = decide_time(title, description, row, override)
    knife = decide_knife(title, description, tags, row, override)
    heat = decide_heat(title, description, row, override)
    frying_pan = decide_frying_pan(title, description, row)
    microwave = decide_microwave(title, description)

    decisions = {
        "genre": genre,
        "staple": staple,
        "dish_shape": dish_shape,
        "main_ingredient": main_ingredient,
        "taste_tag": taste,
        "temperature_tag": temperature,
        "time_tag": time,
        "uses_knife_tag": knife,
        "uses_heat_tag": heat,
        "uses_frying_pan": frying_pan,
        "uses_microwave": microwave,
    }
    status, reasons = review_status(decisions, master_confirmed)

    output: dict[str, str] = {}
    for key, decision in decisions.items():
        output[key] = decision.value
        output[f"{key}_confidence"] = f"{decision.confidence:.2f}"
        output[f"{key}_basis"] = decision.basis
    output["tag_review_status"] = status
    output["tag_review_reasons"] = "; ".join(reasons)
    output["tag_basis_json"] = json.dumps(
        {
            key: {
                "value": decision.value,
                "confidence": decision.confidence,
                "basis": decision.basis,
            }
            for key, decision in decisions.items()
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return output
