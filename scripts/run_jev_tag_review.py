"""Use Jev to review low-confidence recipe feature tags.

This script does not overwrite the app database. It writes Jev's decisions to
data/jev-tag-results.csv so humans can inspect or apply them later.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from collect_youtube_api_recipes import load_local_env


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENDPOINT = "https://api.typesafe.ai/v1/systemone"

GENRE_LABELS = {
    "washoku": "和食",
    "yoshoku": "洋食",
    "chuka": "中華",
    "korean": "韓国",
    "other": "その他",
}
STAPLE_LABELS = {
    "rice": "ご飯",
    "noodle": "麺",
    "bread": "パン",
    "other": "その他",
}
DISH_SHAPE_LABELS = {
    "bowl": "丼",
    "rice_other": "丼以外のご飯もの",
    "noodle": "麺料理",
    "bread": "パン料理",
    "main": "主菜",
    "stew": "煮込み",
    "other": "その他",
}
MAIN_INGREDIENT_LABELS = {
    "meat": "肉",
    "fish": "魚",
    "egg": "卵",
    "soy": "豆腐・大豆",
    "vegetable": "野菜中心",
    "other": "その他",
}
TASTE_LABELS = {
    "rich": "ガッツリ",
    "semi_rich": "ややガッツリ",
    "semi_light": "ややあっさり",
    "light": "あっさり",
}
TEMPERATURE_LABELS = {
    "warm": "温かい",
    "cold": "冷たい",
}
TIME_LABELS = {
    "within_15": "15分以内",
    "min_15_30": "15〜30分",
    "over_30": "30分以上",
}


OUTPUT_COLUMNS = [
    "video_id",
    "メニュー",
    "動画URL",
    "jev_status",
    "jev_review_status",
    "is_single_recipe",
    "is_single_recipe_confidence",
    "genre",
    "genre_confidence",
    "staple",
    "staple_confidence",
    "dish_shape",
    "dish_shape_confidence",
    "main_ingredient",
    "main_ingredient_confidence",
    "taste_tag",
    "taste_tag_confidence",
    "temperature_tag",
    "temperature_tag_confidence",
    "time_tag",
    "time_tag_confidence",
    "uses_knife_tag",
    "uses_knife_tag_confidence",
    "uses_heat_tag",
    "uses_heat_tag_confidence",
    "uses_frying_pan",
    "uses_frying_pan_confidence",
    "uses_microwave",
    "uses_microwave_confidence",
    "low_confidence_fields",
    "input_tokens",
    "jev_answers_json",
    "error",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as csv_file:
        return list(csv.DictReader(csv_file))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows({column: row.get(column, "") for column in OUTPUT_COLUMNS} for row in rows)


def load_existing_results(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    return read_csv(path)


def load_records_by_id(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    records = json.loads(path.read_text(encoding="utf-8"))
    return {record.get("video_id", ""): record for record in records if record.get("video_id")}


def existing_done_ids(rows: list[dict[str, str]]) -> set[str]:
    return {row.get("video_id", "") for row in rows if row.get("video_id") and row.get("jev_status") == "ok"}


def build_state(row: dict[str, str], source_record: dict | None) -> dict:
    source_record = source_record or {}
    description = (source_record.get("description") or "")[:1800]
    return {
        "title": row.get("メニュー", ""),
        "url": row.get("動画URL", ""),
        "creator": row.get("投稿者", ""),
        "description": description,
        "ingredient_tags": row.get("詳細食材タグ", ""),
        "current_rule_tags": {
            "genre": row.get("genre", ""),
            "staple": row.get("staple", ""),
            "dish_shape": row.get("dish_shape", ""),
            "main_ingredient": row.get("main_ingredient", ""),
            "temperature": row.get("temperature_tag", ""),
            "time": row.get("time_tag", ""),
            "uses_knife": row.get("uses_knife_tag", ""),
            "uses_heat": row.get("uses_heat_tag", ""),
            "uses_frying_pan": row.get("uses_frying_pan", ""),
            "uses_microwave": row.get("uses_microwave", ""),
        },
        "current_rule_reasons": row.get("tag_review_reasons", ""),
        "important_policy": [
            "Judge the actual recipe in this video, not unrelated links, channel promos, or other recommended videos in the description.",
            "Do not treat Japanese connective endings such as したら or だったら as cod fish.",
            "Do not classify ワンパン or フライパン as bread.",
            "If this is a vlog, meal log, storage tip, eating-only video, or multi-recipe compilation rather than one usable recipe, mark is_single_recipe low.",
        ],
    }


def core_questions() -> dict:
    return {
        "is_single_recipe": {
            "type": "noul",
            "instructions": "Is this a single usable cooking recipe video rather than a vlog, food diary, eating-only video, storage tip, or multi-recipe compilation?",
        },
        "genre": {
            "type": "choice",
            "instructions": "Choose the recipe genre from the actual dish.",
            "criteria": {
                "washoku": "Japanese style, including donburi, udon, soba, miso, soy-sauce/teriyaki, dashi, tofu dishes, Japanese home cooking.",
                "yoshoku": "Western or Japanese-Western style, including pasta, gratin, doria, omurice, hamburger steak, curry, toast, sandwich, pizza.",
                "chuka": "Chinese style, including fried rice, gyoza, mapo, ramen, yakisoba, tantanmen, stir-fried Chinese dishes.",
                "korean": "Korean style, including kimchi, bibimbap, chijimi, namul, gochujang, yangnyeom, sundubu.",
                "other": "None of the above or not enough evidence.",
            },
        },
        "staple": {
            "type": "choice",
            "instructions": "Choose the staple category of the actual dish.",
            "criteria": {
                "rice": "Rice is central, including rice bowl, fried rice, omurice, risotto, rice balls, zosui.",
                "noodle": "Noodles are central, including udon, soba, ramen, pasta, somen, yakisoba, harusame, pho.",
                "bread": "Bread is central, including toast, sandwich, burger, pizza, hot dog. Do not count frying pan or one-pan as bread.",
                "other": "No central rice, noodle, or bread.",
            },
        },
        "dish_shape": {
            "type": "choice",
            "instructions": "Choose the recipe form from the actual dish.",
            "criteria": {
                "bowl": "Donburi or rice bowl: something served on top of rice.",
                "rice_other": "Rice dish that is not a bowl, such as risotto, zosui, fried rice, omurice, rice ball, doria.",
                "noodle": "Noodle dish.",
                "bread": "Bread dish.",
                "main": "Main dish or side dish with protein/vegetables, not centered on rice/noodles/bread.",
                "stew": "Stewed/simmered dish, curry, stew, nikomi, nabe-like dish.",
                "other": "Dessert, snack, drink, unclear, or no fit.",
            },
        },
        "main_ingredient": {
            "type": "choice",
            "instructions": "Choose the central ingredient impression. Prefer the ingredient the user would feel the dish is mainly about.",
            "criteria": {
                "meat": "Beef, pork, chicken, minced meat, ham, bacon, sausage are central.",
                "fish": "Fish or seafood is central, including tuna, shrimp, shellfish, mentaiko.",
                "egg": "Egg is central, including omurice/fried rice/omelet when egg is the strongest impression.",
                "soy": "Tofu, atsuage, aburaage, natto, soy products are central.",
                "vegetable": "Vegetables are central and not just garnish.",
                "other": "Dairy, cheese, sweets, staple-only, seasoning-only, or unclear.",
            },
        },
        "taste_tag": {
            "type": "choice",
            "instructions": "Choose the taste heaviness/richness from ingredients, cooking method, and dish name.",
            "criteria": {
                "rich": "Very rich/heavy: fried, cheesy, mayo/butter-heavy, fatty meat, strong sauce.",
                "semi_rich": "Somewhat rich: meat, egg, oil, sauce, pasta, stir-fry but not extremely heavy.",
                "semi_light": "Somewhat light: simple protein/vegetable, moderate seasoning, not oily.",
                "light": "Light/refreshing: salad, cold tofu, soup, steamed/boiled, low oil.",
            },
        },
    }


def workload_questions() -> dict:
    return {
        "temperature_tag": {
            "type": "choice",
            "instructions": "Choose whether the dish is normally eaten warm or cold.",
            "criteria": {
                "warm": "Normally served warm/hot. Rice and bread dishes are warm unless clearly cold.",
                "cold": "Normally served cold/chilled, such as salad, cold noodles, chilled tofu, chilled dessert.",
            },
        },
        "time_tag": {
            "type": "choice",
            "instructions": "Choose likely cooking time. Use explicit minutes if present.",
            "criteria": {
                "within_15": "15 minutes or less.",
                "min_15_30": "More than 15 minutes and up to 30 minutes.",
                "over_30": "More than 30 minutes.",
            },
        },
        "uses_knife_tag": {
            "type": "noul",
            "instructions": "Does this recipe likely require using a knife or cutting ingredients? If the title says knife-free/cut-free, answer no.",
        },
        "uses_heat_tag": {
            "type": "noul",
            "instructions": "Does this recipe use heat, including stove, oven, toaster, microwave heating, boiling, frying, or grilling?",
        },
        "uses_frying_pan": {
            "type": "noul",
            "instructions": "Does this recipe use a frying pan or pan cooking? One-pan and stir-fry count as yes. Microwave-only, toaster-only, and no-heat recipes count as no.",
        },
        "uses_microwave": {
            "type": "noul",
            "instructions": "Does this recipe use a microwave? レンジ and レンチン count as yes.",
        },
    }


def call_jev(endpoint: str, api_key: str, state: dict, questions: dict, idempotency_key: str) -> dict:
    body_text = json.dumps(
        {
            "model": "jev-latest",
            "state": state,
            "questions": questions,
        },
        ensure_ascii=False,
    )
    body = body_text.encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Idempotency-Key": idempotency_key,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        if "CERTIFICATE_VERIFY_FAILED" not in repr(exc):
            raise
        return call_jev_with_curl(endpoint, api_key, body_text, idempotency_key)


def call_jev_with_curl(endpoint: str, api_key: str, body_text: str, idempotency_key: str) -> dict:
    result = subprocess.run(
        [
            "curl",
            "-sS",
            "-X",
            "POST",
            endpoint,
            "-H",
            f"Authorization: Bearer {api_key}",
            "-H",
            "Content-Type: application/json",
            "-H",
            f"Idempotency-Key: {idempotency_key}",
            "--data-binary",
            "@-",
        ],
        input=body_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr[:500]}")
    response = json.loads(result.stdout)
    if "error" in response:
        raise RuntimeError(json.dumps(response["error"], ensure_ascii=False))
    return response


def choice_value(answer: dict, labels: dict[str, str]) -> tuple[str, str]:
    key = answer.get("choice") or ""
    confidence = answer.get("confidence")
    if confidence is None:
        probabilities = answer.get("probabilities") or {}
        confidence = probabilities.get(key, 0)
    return labels.get(key, key), f"{float(confidence or 0):.2f}"


def noul_value(answer: dict) -> tuple[str, str]:
    probability = float(answer.get("noul", 0))
    value = probability >= 0.5
    confidence = max(probability, 1 - probability)
    return str(value).lower(), f"{confidence:.2f}"


def build_output_row(
    review_row: dict[str, str],
    core_response: dict,
    workload_response: dict,
    accept_threshold: float,
) -> dict[str, str]:
    core_answers = core_response.get("answers", {})
    workload_answers = workload_response.get("answers", {})
    output = {
        "video_id": review_row.get("video_id", ""),
        "メニュー": review_row.get("メニュー", ""),
        "動画URL": review_row.get("動画URL", ""),
        "jev_status": "ok",
        "error": "",
    }

    output["is_single_recipe"], output["is_single_recipe_confidence"] = noul_value(core_answers.get("is_single_recipe", {}))
    output["genre"], output["genre_confidence"] = choice_value(core_answers.get("genre", {}), GENRE_LABELS)
    output["staple"], output["staple_confidence"] = choice_value(core_answers.get("staple", {}), STAPLE_LABELS)
    output["dish_shape"], output["dish_shape_confidence"] = choice_value(core_answers.get("dish_shape", {}), DISH_SHAPE_LABELS)
    output["main_ingredient"], output["main_ingredient_confidence"] = choice_value(core_answers.get("main_ingredient", {}), MAIN_INGREDIENT_LABELS)
    output["taste_tag"], output["taste_tag_confidence"] = choice_value(core_answers.get("taste_tag", {}), TASTE_LABELS)
    output["temperature_tag"], output["temperature_tag_confidence"] = choice_value(workload_answers.get("temperature_tag", {}), TEMPERATURE_LABELS)
    output["time_tag"], output["time_tag_confidence"] = choice_value(workload_answers.get("time_tag", {}), TIME_LABELS)
    output["uses_knife_tag"], output["uses_knife_tag_confidence"] = noul_value(workload_answers.get("uses_knife_tag", {}))
    output["uses_heat_tag"], output["uses_heat_tag_confidence"] = noul_value(workload_answers.get("uses_heat_tag", {}))
    output["uses_frying_pan"], output["uses_frying_pan_confidence"] = noul_value(workload_answers.get("uses_frying_pan", {}))
    output["uses_microwave"], output["uses_microwave_confidence"] = noul_value(workload_answers.get("uses_microwave", {}))

    confidence_fields = [
        "is_single_recipe_confidence",
        "genre_confidence",
        "staple_confidence",
        "dish_shape_confidence",
        "main_ingredient_confidence",
        "taste_tag_confidence",
        "temperature_tag_confidence",
        "time_tag_confidence",
        "uses_knife_tag_confidence",
        "uses_heat_tag_confidence",
        "uses_frying_pan_confidence",
        "uses_microwave_confidence",
    ]
    low_confidence_fields = [
        field.replace("_confidence", "")
        for field in confidence_fields
        if float(output.get(field) or 0) < accept_threshold
    ]
    if output.get("is_single_recipe") == "false" and float(output.get("is_single_recipe_confidence") or 0) >= accept_threshold:
        output["jev_review_status"] = "exclude_candidate"
    elif low_confidence_fields:
        output["jev_review_status"] = "needs_review"
    else:
        output["jev_review_status"] = "ai_tagged"
    output["low_confidence_fields"] = ";".join(low_confidence_fields)
    output["input_tokens"] = str(
        int(core_response.get("usage", {}).get("input_tokens") or 0)
        + int(workload_response.get("usage", {}).get("input_tokens") or 0)
    )
    output["jev_answers_json"] = json.dumps(
        {
            "core": core_answers,
            "workload": workload_answers,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return output


def error_row(review_row: dict[str, str], error: str) -> dict[str, str]:
    return {
        "video_id": review_row.get("video_id", ""),
        "メニュー": review_row.get("メニュー", ""),
        "動画URL": review_row.get("動画URL", ""),
        "jev_status": "error",
        "jev_review_status": "needs_review",
        "error": error,
    }


def upsert_result(rows: list[dict[str, str]], new_row: dict[str, str]) -> None:
    video_id = new_row.get("video_id", "")
    rows[:] = [row for row in rows if row.get("video_id", "") != video_id]
    rows.append(new_row)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review low-confidence recipe tags with Jev.")
    parser.add_argument("--review-input", default="data/recipe-tag-review.csv")
    parser.add_argument("--records-input", default="data/youtube_api_recipes.json")
    parser.add_argument("--output", default="data/jev-tag-results.csv")
    parser.add_argument("--endpoint", default=os.environ.get("JEV_API_URL", DEFAULT_ENDPOINT))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--sleep", type=float, default=0.6)
    parser.add_argument("--accept-threshold", type=float, default=0.75)
    parser.add_argument("--resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    return parser


def main() -> None:
    load_local_env(ROOT / ".env")
    args = build_parser().parse_args()
    api_key = os.environ.get("JEV_API_KEY") or os.environ.get("JEVMODEL_API_KEY")
    if not api_key:
        raise SystemExit("JEV_API_KEY is missing. Add it to .env first.")

    review_rows = read_csv(ROOT / args.review_input)
    if args.offset:
        review_rows = review_rows[args.offset :]
    if args.limit:
        review_rows = review_rows[: args.limit]

    output_path = ROOT / args.output
    results = load_existing_results(output_path) if args.resume else []
    done_ids = existing_done_ids(results) if args.resume else set()
    records_by_id = load_records_by_id(ROOT / args.records_input)

    attempted = 0
    for index, review_row in enumerate(review_rows, 1):
        video_id = review_row.get("video_id", "")
        if video_id in done_ids:
            continue

        state = build_state(review_row, records_by_id.get(video_id))
        try:
            core_response = call_jev(
                args.endpoint,
                api_key,
                state,
                core_questions(),
                f"{video_id}-core-v1",
            )
            if args.sleep:
                time.sleep(args.sleep)
            workload_response = call_jev(
                args.endpoint,
                api_key,
                state,
                workload_questions(),
                f"{video_id}-workload-v1",
            )
            upsert_result(results, build_output_row(review_row, core_response, workload_response, args.accept_threshold))
            attempted += 1
            print(f"[{index}/{len(review_rows)}] ok {video_id}", flush=True)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            upsert_result(results, error_row(review_row, f"HTTP {exc.code}: {body[:500]}"))
            print(f"[{index}/{len(review_rows)}] error {video_id}: HTTP {exc.code}", flush=True)
            write_csv(output_path, results)
            if exc.code in {401, 402, 422}:
                raise SystemExit(1)
        except Exception as exc:
            upsert_result(results, error_row(review_row, repr(exc)))
            print(f"[{index}/{len(review_rows)}] error {video_id}: {exc!r}", flush=True)
            write_csv(output_path, results)
            raise

        write_csv(output_path, results)
        if args.sleep:
            time.sleep(args.sleep)

    print(f"Saved {len(results)} rows to {output_path}")
    print(f"Attempted {attempted} new rows")


if __name__ == "__main__":
    main()
