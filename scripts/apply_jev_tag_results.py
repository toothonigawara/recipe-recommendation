"""Apply high-confidence Jev tag review results to generated recipe datasets.

This only updates the added feature-tag columns and featureTags object.
Existing recommender columns such as taste/time/temperature/knife/heat are left
unchanged so the current recommendation UI keeps working.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from build_recipe_dataset import write_js, write_json


FIELD_PAIRS = {
    "genre": "genre_confidence",
    "staple": "staple_confidence",
    "dish_shape": "dish_shape_confidence",
    "main_ingredient": "main_ingredient_confidence",
    "taste_tag": "taste_tag_confidence",
    "temperature_tag": "temperature_tag_confidence",
    "time_tag": "time_tag_confidence",
    "uses_knife_tag": "uses_knife_tag_confidence",
    "uses_heat_tag": "uses_heat_tag_confidence",
    "uses_frying_pan": "uses_frying_pan_confidence",
    "uses_microwave": "uses_microwave_confidence",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as csv_file:
        return list(csv.DictReader(csv_file))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def confidence(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def rebuild_basis_json(row: dict[str, str]) -> str:
    keys = [
        "genre",
        "staple",
        "dish_shape",
        "main_ingredient",
        "taste_tag",
        "temperature_tag",
        "time_tag",
        "uses_knife_tag",
        "uses_heat_tag",
        "uses_frying_pan",
        "uses_microwave",
    ]
    return json.dumps(
        {
            key: {
                "value": row.get(key, ""),
                "confidence": confidence(row.get(f"{key}_confidence", "")),
                "basis": row.get(f"{key}_basis", ""),
            }
            for key in keys
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def apply_results(rows: list[dict[str, str]], jev_rows: list[dict[str, str]], threshold: float) -> tuple[int, int, int]:
    jev_by_id = {row.get("video_id", ""): row for row in jev_rows if row.get("jev_status") == "ok"}
    updated_rows = 0
    updated_fields = 0
    exclude_candidates = 0

    for row in rows:
        if row.get("fact_status") == "confirmed" or row.get("tag_review_status") == "confirmed":
            continue
        result = jev_by_id.get(row.get("video_id", ""))
        if not result:
            continue

        row_updated = False
        if result.get("jev_review_status") == "exclude_candidate":
            row["tag_review_status"] = "exclude_candidate"
            row["tag_review_reasons"] = "JEV: 単体の完成レシピ動画ではない可能性が高い"
            exclude_candidates += 1
            row_updated = True

        for field, confidence_field in FIELD_PAIRS.items():
            value = result.get(field, "")
            score = confidence(result.get(confidence_field, ""))
            if not value or score < threshold:
                continue
            row[field] = value
            row[confidence_field] = f"{score:.2f}"
            row[f"{field}_basis"] = "JEV判定"
            updated_fields += 1
            row_updated = True

        if row_updated:
            if row.get("tag_review_status") != "exclude_candidate":
                row["tag_review_status"] = result.get("jev_review_status", row.get("tag_review_status", ""))
                row["tag_review_reasons"] = result.get("low_confidence_fields", "")
            row["tag_basis_json"] = rebuild_basis_json(row)
            updated_rows += 1

    return updated_rows, updated_fields, exclude_candidates


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Apply high-confidence Jev tag results.")
    parser.add_argument("--csv-input", default="data/2000件料理レシピ.csv")
    parser.add_argument("--json-output", default="data/2000_recipes_scored.json")
    parser.add_argument("--js-output", default="recipes-data.js")
    parser.add_argument("--jev-results", default="data/jev-tag-results.csv")
    parser.add_argument("--threshold", type=float, default=0.75)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = read_csv(Path(args.csv_input))
    jev_rows = read_csv(Path(args.jev_results))
    updated_rows, updated_fields, exclude_candidates = apply_results(rows, jev_rows, args.threshold)
    write_csv(Path(args.csv_input), rows)
    write_json(Path(args.json_output), rows)
    write_js(Path(args.js_output), rows)
    print(f"Updated rows: {updated_rows}")
    print(f"Updated fields: {updated_fields}")
    print(f"Exclude candidates: {exclude_candidates}")


if __name__ == "__main__":
    main()
