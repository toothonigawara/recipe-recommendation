"""Ingredient category scoring helpers for recipe CSV data.

This module is intentionally small and dependency-free so it can be imported
from a Flask app or used as a command line script.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable


DEFAULT_CATEGORY_SCORE = 5
DEFAULT_AXIS_SCORE = 5
DEFAULT_STANDARD_SERVING_G = 100

INGREDIENT_SERVING_STANDARDS_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "ingredient-serving-standards.csv"
)

# さっぱり寄りを低く、こってり寄りを高く置いた食材カテゴリスコア。
CATEGORY_SCORES = {
    "葉物野菜": 1,
    "きのこ": 2,
    "根菜": 3,
    "豆腐・大豆系": 3,
    "魚介": 4,
    "卵": 5,
    "米": 6,
    "麺": 6,
    "鶏肉": 6,
    "肉類": 8,
    "チーズ・バター・マヨ系": 10,
}

# 表記ゆれがCSVに入っても同じカテゴリとして扱うための別名。
CATEGORY_ALIASES = {
    "葉物": "葉物野菜",
    "野菜": "葉物野菜",
    "きのこ類": "きのこ",
    "キノコ": "きのこ",
    "豆腐": "豆腐・大豆系",
    "大豆": "豆腐・大豆系",
    "豆・豆腐": "豆腐・大豆系",
    "魚": "魚介",
    "魚介類": "魚介",
    "卵類": "卵",
    "ご飯": "米",
    "ご飯・米": "米",
    "麺類": "麺",
    "豚肉・牛肉": "肉類",
    "豚肉": "肉類",
    "牛肉": "肉類",
    "挽肉": "肉類",
    "ひき肉": "肉類",
    "チーズ・バター系": "チーズ・バター・マヨ系",
    "チーズ・バター・マヨ": "チーズ・バター・マヨ系",
    "チーズ・バター・マヨネーズ系": "チーズ・バター・マヨ系",
}

# 詳細食材タグから研究用カテゴリへ変換する対応表。
# 個別材料自体は点数化せず、必ずカテゴリの点数として扱う。
TAG_CATEGORY_MAP = {
    "cabbage": "葉物野菜",
    "asparagus": "葉物野菜",
    "cucumber": "葉物野菜",
    "bitter_melon": "葉物野菜",
    "green_bean": "葉物野菜",
    "shishito": "葉物野菜",
    "komatsuna": "葉物野菜",
    "chrysanthemum": "葉物野菜",
    "celery": "葉物野菜",
    "bamboo_shoot": "葉物野菜",
    "bok_choy": "葉物野菜",
    "winter_melon": "葉物野菜",
    "tomato": "葉物野菜",
    "eggplant": "葉物野菜",
    "napa_cabbage": "葉物野菜",
    "nira": "葉物野菜",
    "green_onion": "葉物野菜",
    "bell_pepper": "葉物野菜",
    "broccoli": "葉物野菜",
    "spinach": "葉物野菜",
    "bean_sprouts": "葉物野菜",
    "lettuce": "葉物野菜",
    "enoki": "きのこ",
    "shimeji": "きのこ",
    "shiitake": "きのこ",
    "dried_shiitake": "きのこ",
    "jellyfish": "きのこ",
    "turnip": "根菜",
    "pumpkin": "根菜",
    "burdock": "根菜",
    "sweet_potato": "根菜",
    "taro": "根菜",
    "potato": "根菜",
    "daikon": "根菜",
    "onion": "根菜",
    "nagaimo": "根菜",
    "carrot": "根菜",
    "corn": "根菜",
    "lotus_root": "根菜",
    "konnyaku": "根菜",
    "ginger": "根菜",
    "garlic": "根菜",
    "tofu": "豆腐・大豆系",
    "atsuage": "豆腐・大豆系",
    "aburaage": "豆腐・大豆系",
    "soybean": "豆腐・大豆系",
    "natto": "豆腐・大豆系",
    "okara": "豆腐・大豆系",
    "aji": "魚介",
    "squid": "魚介",
    "sardine": "魚介",
    "shrimp": "魚介",
    "shellfish": "魚介",
    "oyster": "魚介",
    "crab": "魚介",
    "salmon": "魚介",
    "mackerel": "魚介",
    "saury": "魚介",
    "shirasu": "魚介",
    "whitefish": "魚介",
    "octopus": "魚介",
    "yellowtail": "魚介",
    "scallop": "魚介",
    "tuna_sashimi": "魚介",
    "canned_tuna": "魚介",
    "mentaiko": "魚介",
    "fried_fishcake": "魚介",
    "chikuwa": "魚介",
    "wakame": "葉物野菜",
    "kombu": "葉物野菜",
    "hijiki": "葉物野菜",
    "mozuku": "葉物野菜",
    "seaweed_salad": "葉物野菜",
    "egg": "卵",
    "quail_egg": "卵",
    "rice": "米",
    "udon": "麺",
    "soba": "麺",
    "noodles": "麺",
    "somen": "麺",
    "ramen": "麺",
    "yakisoba_noodles": "麺",
    "rice_noodles": "麺",
    "pasta": "麺",
    "harusame": "麺",
    "bread": "米",
    "flour": "米",
    "chicken": "鶏肉",
    "beef": "肉類",
    "pork": "肉類",
    "minced_meat": "肉類",
    "ham": "肉類",
    "bacon": "肉類",
    "cheese": "チーズ・バター・マヨ系",
    "butter": "チーズ・バター・マヨ系",
    "mayonnaise": "チーズ・バター・マヨ系",
    "milk": "チーズ・バター・マヨ系",
    "curry_roux": "チーズ・バター・マヨ系",
}

# 味スコアの仮モデルで使う重み。
RICHNESS_WEIGHTS = {
    "ingredient": 0.6,
    "oil": 0.3,
    "creator": 0.1,
}


def load_ingredient_serving_standards(
    csv_path: str | Path = INGREDIENT_SERVING_STANDARDS_PATH,
) -> dict[str, dict[str, str]]:
    """食材ごとの1人前基準量と単位換算表を読み込む。"""
    path = Path(csv_path)
    if not path.exists():
        return {}

    with path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        return {row["tag"]: row for row in reader if row.get("tag")}


INGREDIENT_SERVING_STANDARDS = load_ingredient_serving_standards()


def normalize_category_name(category_name: str | None) -> str:
    """カテゴリ名の空白と表記ゆれを整える。"""
    if category_name is None:
        return ""

    normalized = str(category_name).strip()
    return CATEGORY_ALIASES.get(normalized, normalized)


def get_category_score(category_name: str | None) -> int:
    """カテゴリ名を受け取り、1から10点のスコアを返す。

    未登録カテゴリや空欄は中間値の5点として扱う。
    """
    normalized = normalize_category_name(category_name)
    return CATEGORY_SCORES.get(normalized, DEFAULT_CATEGORY_SCORE)


def split_category_text(category_text: str | None) -> list[str]:
    """セミコロン区切りのカテゴリ文字列をカテゴリ名の配列にする。"""
    if category_text is None:
        return []

    text = str(category_text).strip()
    if not text:
        return []

    # 全角セミコロンも許容し、空要素は除外する。
    return [item.strip() for item in text.replace("；", ";").split(";") if item.strip()]


def split_tag_text(tag_text: str | None) -> list[str]:
    """カンマ区切りの詳細食材タグを配列にする。"""
    if tag_text is None:
        return []

    text = str(tag_text).strip()
    if not text:
        return []

    normalized = text.replace("，", ",").replace("、", ",").replace("；", ",").replace(";", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def generate_ingredient_categories(tag_text: str | None) -> str:
    """詳細食材タグからingredient_categories用のカテゴリ文字列を作る。

    例:
    pork,rice,egg,green_onion -> 肉類;米;卵;葉物野菜
    """
    categories = []
    seen_categories = set()

    for tag in split_tag_text(tag_text):
        category = TAG_CATEGORY_MAP.get(tag)
        if category and category not in seen_categories:
            categories.append(category)
            seen_categories.add(category)

    return ";".join(categories)


def calculate_ingredient_score(category_text: str | None) -> float:
    """料理全体の材料スコアを計算する。

    複数カテゴリがある場合:
    材料スコア = 平均点 * 0.7 + 最大点 * 0.3

    空欄の場合は中間値の5点を返す。
    """
    categories = split_category_text(category_text)
    if not categories:
        return float(DEFAULT_CATEGORY_SCORE)

    scores = [get_category_score(category) for category in categories]
    average_score = sum(scores) / len(scores)
    max_score = max(scores)
    ingredient_score = average_score * 0.7 + max_score * 0.3

    # 研究資料やCSVで読みやすいように小数第2位までにする。
    return round(ingredient_score, 2)


def get_ingredient_standard(tag: str | None) -> dict[str, str]:
    """食材タグに対応する1人前基準表の行を返す。"""
    if tag is None:
        return {}
    return INGREDIENT_SERVING_STANDARDS.get(str(tag).strip(), {})


def get_standard_serving_grams(tag: str | None) -> float:
    """食材タグの1人前基準量をgで返す。未登録なら100g。"""
    standard = get_ingredient_standard(tag)
    return parse_number(standard.get("standard_serving_g"), default=DEFAULT_STANDARD_SERVING_G)


def convert_quantity_to_grams(tag: str | None, quantity: str | int | float | None, unit: str = "g") -> float:
    """食材量をgに変換する。

    例:
    - pork, 400, g -> 400g
    - onion, 0.5, 個 -> 100g  # 玉ねぎ1個=200g換算
    - egg, 2, 個 -> 100g      # 卵1個=50g換算
    """
    amount = parse_number(quantity, default=0)
    normalized_unit = str(unit or "g").strip()
    if amount <= 0:
        return 0

    if normalized_unit in {"g", "グラム"}:
        return amount
    if normalized_unit in {"kg", "キロ"}:
        return amount * 1000
    if normalized_unit in {"ml", "cc"}:
        return amount

    standard = get_ingredient_standard(tag)
    unit_name = standard.get("unit_name")
    unit_g = parse_number(standard.get("unit_g"), default=0)
    if unit_name and normalized_unit == unit_name and unit_g > 0:
        return amount * unit_g

    # 未登録単位は暫定的に数値をgとして扱う。
    return amount


def calculate_amount_adjusted_ingredient_score(
    tag: str,
    total_quantity: str | int | float,
    unit: str,
    servings: str | int | float,
) -> float:
    """1食材の量補正済み材料スコアを返す。

    category_scoreは、その食材の標準1人前量を食べたときの点数とみなす。
    例: pork 400g / 2人前 = 200g。豚肉の標準量200gなので、肉類8点をそのまま使う。
    """
    serving_count = max(1, parse_number(servings, default=1))
    total_g = convert_quantity_to_grams(tag, total_quantity, unit)
    per_serving_g = total_g / serving_count
    standard_g = max(1, get_standard_serving_grams(tag))

    category = TAG_CATEGORY_MAP.get(tag)
    base_score = get_category_score(category)
    amount_ratio = per_serving_g / standard_g
    adjusted_score = base_score * amount_ratio
    return round(clamp_score(adjusted_score), 2)


def calculate_amount_adjusted_ingredient_score_from_items(
    items: Iterable[dict[str, str]],
    servings: str | int | float,
) -> float:
    """複数食材の量補正済み材料スコアを計算する。

    itemsの形式:
    [{"tag": "pork", "quantity": "400", "unit": "g"}, ...]

    料理全体のまとめ方は既存式と同じ:
    材料スコア = 平均点 * 0.7 + 最大点 * 0.3
    """
    scores = []
    for item in items:
        tag = item.get("tag", "")
        if tag not in TAG_CATEGORY_MAP:
            continue
        scores.append(
            calculate_amount_adjusted_ingredient_score(
                tag,
                item.get("quantity", 0),
                item.get("unit", "g"),
                servings,
            )
        )

    if not scores:
        return float(DEFAULT_CATEGORY_SCORE)

    average_score = sum(scores) / len(scores)
    max_score = max(scores)
    return round(average_score * 0.7 + max_score * 0.3, 2)


def parse_number(value: str | int | float | None, default: float = DEFAULT_AXIS_SCORE) -> float:
    """CSVの文字列から数値を取り出す。空欄や不正値はdefaultにする。"""
    if value is None:
        return default

    text = str(value).strip()
    if not text:
        return default

    try:
        return float(text)
    except ValueError:
        return default


def clamp_score(score: float, minimum: float = 1, maximum: float = 10) -> float:
    """スコアを1から10の範囲に収める。"""
    return max(minimum, min(maximum, score))


def get_oil_score(oil_value: str | int | float | None) -> float:
    """油感を1から10点に変換する。

    CSVの油感が1から5段階の場合は2倍し、すでに10点満点の場合はそのまま使う。
    """
    oil = parse_number(oil_value, default=3)
    if oil <= 5:
        oil *= 2
    return clamp_score(oil)


def get_creator_score(creator_text: str | None) -> int:
    """投稿者や特徴テキストから、投稿者傾向の仮スコアを返す。

    現段階では厳密な学習モデルではなく、研究プロトタイプ用のルールベース。
    """
    text = "" if creator_text is None else str(creator_text)

    if any(keyword in text for keyword in ("リュウジ", "バズレシピ", "だれウマ", "がっつり", "ガッツリ", "濃い")):
        return 8
    if any(keyword in text for keyword in ("コウケンテツ", "Koh", "家庭", "丁寧")):
        return 5
    if any(keyword in text for keyword in ("DELISH", "デリッシュ", "クラシル", "Kurashiru", "macaroni", "マカロニ", "初心者", "簡単")):
        return 4
    if any(keyword in text for keyword in ("ダイエット", "さっぱり", "ヘルシー")):
        return 3

    return DEFAULT_AXIS_SCORE


def get_row_value(row: dict[str, str], candidates: Iterable[str]) -> str | None:
    """候補列名のうち、最初に見つかった値を返す。"""
    for column_name in candidates:
        if column_name in row:
            return row.get(column_name)
    return None


def calculate_richness_score(
    row: dict[str, str],
    category_column: str = "ingredient_categories",
    ingredient_score_column: str = "ingredient_score",
    oil_columns: Iterable[str] = ("油感", "油感（油の量）", "oil_score", "oil"),
    creator_columns: Iterable[str] = ("投稿者", "投稿者の傾向", "creator", "author"),
) -> float:
    """材料・油感・投稿者傾向からrichness_scoreを計算する。

    仮モデル:
    richness_score = 0.6 * 材料 + 0.3 * 油感 + 0.1 * 投稿者
    """
    if row.get(ingredient_score_column):
        ingredient_score = parse_number(row.get(ingredient_score_column))
    else:
        ingredient_score = calculate_ingredient_score(row.get(category_column))

    oil_score = get_oil_score(get_row_value(row, oil_columns))
    creator_score = get_creator_score(get_row_value(row, creator_columns))

    richness_score = (
        ingredient_score * RICHNESS_WEIGHTS["ingredient"]
        + oil_score * RICHNESS_WEIGHTS["oil"]
        + creator_score * RICHNESS_WEIGHTS["creator"]
    )
    return round(richness_score, 2)


def calculate_percentile(sorted_values: list[float], percentile: float) -> float:
    """線形補間でパーセンタイルを求める。

    ExcelやNumPyに近い考え方で、データ数が少ない場合も境界が極端に寄りにくい。
    """
    if not sorted_values:
        raise ValueError("Cannot calculate percentile from empty values.")

    if len(sorted_values) == 1:
        return sorted_values[0]

    position = (len(sorted_values) - 1) * percentile
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(sorted_values) - 1)
    fraction = position - lower_index

    lower_value = sorted_values[lower_index]
    upper_value = sorted_values[upper_index]
    return lower_value + (upper_value - lower_value) * fraction


def calculate_quartiles(scores: Iterable[float]) -> tuple[float, float, float]:
    """richness_scoreの分布からQ1、Q2、Q3を求める。"""
    sorted_scores = sorted(float(score) for score in scores)
    if not sorted_scores:
        raise ValueError("Cannot calculate quartiles from empty scores.")

    q1 = calculate_percentile(sorted_scores, 0.25)
    q2 = calculate_percentile(sorted_scores, 0.50)
    q3 = calculate_percentile(sorted_scores, 0.75)
    return round(q1, 2), round(q2, 2), round(q3, 2)


def classify_taste_level(score: float, q1: float, q2: float, q3: float) -> str:
    """四分位数を境界に、味の4段階分類を返す。"""
    if score < q1:
        return "あっさり"
    if score < q2:
        return "ややあっさり"
    if score < q3:
        return "ややがっつり"
    return "がっつり"


def add_ingredient_score_to_rows(
    rows: Iterable[dict[str, str]],
    source_column: str = "ingredient_categories",
    output_column: str = "ingredient_score",
) -> list[dict[str, str]]:
    """CSVから読み込んだ行データに材料スコア列を追加する。"""
    scored_rows = []
    for row in rows:
        scored_row = dict(row)
        scored_row[output_column] = str(calculate_ingredient_score(row.get(source_column)))
        scored_rows.append(scored_row)
    return scored_rows


def add_ingredient_categories_to_rows(
    rows: Iterable[dict[str, str]],
    tag_column: str = "詳細食材タグ",
    output_column: str = "ingredient_categories",
) -> list[dict[str, str]]:
    """詳細食材タグからingredient_categories列を追加する。"""
    categorized_rows = []
    for row in rows:
        categorized_row = dict(row)
        categorized_row[output_column] = generate_ingredient_categories(row.get(tag_column))
        categorized_rows.append(categorized_row)
    return categorized_rows


def add_richness_and_taste_level_to_rows(
    rows: Iterable[dict[str, str]],
    category_column: str = "ingredient_categories",
    tag_column: str = "詳細食材タグ",
    ingredient_score_column: str = "ingredient_score",
    richness_score_column: str = "richness_score",
    taste_level_column: str = "taste_level",
) -> list[dict[str, str]]:
    """CSV行にingredient_score、richness_score、taste_levelを追加する。

    taste_levelは全レシピのrichness_scoreを計算したあと、Q1/Q2/Q3で分類する。
    """
    scored_rows = []

    for row in rows:
        scored_row = dict(row)
        if not scored_row.get(category_column) and tag_column in scored_row:
            scored_row[category_column] = generate_ingredient_categories(scored_row.get(tag_column))
        if not scored_row.get(ingredient_score_column):
            scored_row[ingredient_score_column] = str(calculate_ingredient_score(scored_row.get(category_column)))
        scored_row[richness_score_column] = str(
            calculate_richness_score(
                scored_row,
                category_column=category_column,
                ingredient_score_column=ingredient_score_column,
            )
        )
        scored_rows.append(scored_row)

    quartiles = calculate_quartiles(
        parse_number(row[richness_score_column]) for row in scored_rows
    )
    q1, q2, q3 = quartiles

    for row in scored_rows:
        score = parse_number(row[richness_score_column])
        row[taste_level_column] = classify_taste_level(score, q1, q2, q3)

    return scored_rows


def add_ingredient_score_to_csv(
    input_csv_path: str | Path,
    output_csv_path: str | Path,
    source_column: str = "ingredient_categories",
    output_column: str = "ingredient_score",
    encoding: str = "utf-8-sig",
) -> None:
    """CSVを読み込み、材料スコア列を追加して別CSVに保存する。"""
    input_path = Path(input_csv_path)
    output_path = Path(output_csv_path)

    with input_path.open(newline="", encoding=encoding) as input_file:
        reader = csv.DictReader(input_file)
        if reader.fieldnames is None:
            raise ValueError("CSV header was not found.")
        if source_column not in reader.fieldnames:
            raise ValueError(f"CSV must include '{source_column}' column.")

        rows = add_ingredient_score_to_rows(reader, source_column, output_column)
        fieldnames = list(reader.fieldnames)
        if output_column not in fieldnames:
            fieldnames.append(output_column)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding=encoding) as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def add_ingredient_categories_to_csv(
    input_csv_path: str | Path,
    output_csv_path: str | Path,
    tag_column: str = "詳細食材タグ",
    output_column: str = "ingredient_categories",
    encoding: str = "utf-8-sig",
) -> None:
    """CSVを読み込み、ingredient_categories列を追加して別CSVに保存する。"""
    input_path = Path(input_csv_path)
    output_path = Path(output_csv_path)

    with input_path.open(newline="", encoding=encoding) as input_file:
        reader = csv.DictReader(input_file)
        if reader.fieldnames is None:
            raise ValueError("CSV header was not found.")
        if tag_column not in reader.fieldnames:
            raise ValueError(f"CSV must include '{tag_column}' column.")

        rows = add_ingredient_categories_to_rows(reader, tag_column, output_column)
        fieldnames = list(reader.fieldnames)
        if output_column not in fieldnames:
            fieldnames.append(output_column)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding=encoding) as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def add_richness_and_taste_level_to_csv(
    input_csv_path: str | Path,
    output_csv_path: str | Path,
    category_column: str = "ingredient_categories",
    tag_column: str = "詳細食材タグ",
    ingredient_score_column: str = "ingredient_score",
    richness_score_column: str = "richness_score",
    taste_level_column: str = "taste_level",
    encoding: str = "utf-8-sig",
) -> tuple[float, float, float]:
    """CSVにrichness_scoreとtaste_levelを追加して保存する。

    戻り値は分類に使用した(Q1, Q2, Q3)。
    """
    input_path = Path(input_csv_path)
    output_path = Path(output_csv_path)

    with input_path.open(newline="", encoding=encoding) as input_file:
        reader = csv.DictReader(input_file)
        if reader.fieldnames is None:
            raise ValueError("CSV header was not found.")
        if (
            category_column not in reader.fieldnames
            and tag_column not in reader.fieldnames
            and ingredient_score_column not in reader.fieldnames
        ):
            raise ValueError(
                f"CSV must include '{category_column}', '{tag_column}', or '{ingredient_score_column}' column."
            )

        rows = add_richness_and_taste_level_to_rows(
            reader,
            category_column=category_column,
            tag_column=tag_column,
            ingredient_score_column=ingredient_score_column,
            richness_score_column=richness_score_column,
            taste_level_column=taste_level_column,
        )
        q1, q2, q3 = calculate_quartiles(
            parse_number(row[richness_score_column]) for row in rows
        )

        fieldnames = list(reader.fieldnames)
        for column_name in (category_column, ingredient_score_column, richness_score_column, taste_level_column):
            if column_name not in fieldnames:
                fieldnames.append(column_name)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding=encoding) as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return q1, q2, q3


def build_parser() -> argparse.ArgumentParser:
    """コマンドライン実行用の引数を定義する。"""
    parser = argparse.ArgumentParser(
        description="Add ingredient_score, richness_score, and taste_level columns."
    )
    parser.add_argument("input_csv", help="入力CSVのパス")
    parser.add_argument("output_csv", help="出力CSVのパス")
    parser.add_argument(
        "--ingredient-only",
        action="store_true",
        help="ingredient_score列だけを追加する",
    )
    parser.add_argument(
        "--categories-only",
        action="store_true",
        help="詳細食材タグからingredient_categories列だけを追加する",
    )
    parser.add_argument(
        "--tag-column",
        default="詳細食材タグ",
        help="詳細食材タグが入っている列名",
    )
    parser.add_argument(
        "--source-column",
        default="ingredient_categories",
        help="カテゴリ文字列が入っている列名",
    )
    parser.add_argument(
        "--output-column",
        default="ingredient_score",
        help="追加する材料スコア列名",
    )
    parser.add_argument(
        "--richness-column",
        default="richness_score",
        help="追加するrichness_score列名",
    )
    parser.add_argument(
        "--taste-level-column",
        default="taste_level",
        help="追加する味分類列名",
    )
    return parser


def main() -> None:
    """CSVにスコア列と味分類列を追加する。"""
    args = build_parser().parse_args()
    if args.categories_only:
        add_ingredient_categories_to_csv(
            args.input_csv,
            args.output_csv,
            tag_column=args.tag_column,
            output_column=args.source_column,
        )
        return

    if args.ingredient_only:
        add_ingredient_score_to_csv(
            args.input_csv,
            args.output_csv,
            source_column=args.source_column,
            output_column=args.output_column,
        )
        return

    q1, q2, q3 = add_richness_and_taste_level_to_csv(
        args.input_csv,
        args.output_csv,
        category_column=args.source_column,
        tag_column=args.tag_column,
        ingredient_score_column=args.output_column,
        richness_score_column=args.richness_column,
        taste_level_column=args.taste_level_column,
    )
    print(f"Q1={q1}, Q2={q2}, Q3={q3}")


if __name__ == "__main__":
    main()
