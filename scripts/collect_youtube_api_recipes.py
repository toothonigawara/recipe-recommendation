"""Collect recipe videos with YouTube Data API and save JSON/CSV.

Set YOUTUBE_API_KEY before running, or put it in a local .env file:
    export YOUTUBE_API_KEY="..."
    python3 scripts/collect_youtube_api_recipes.py --target-count 1000
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


API_BASE = "https://www.googleapis.com/youtube/v3"
DEFAULT_QUERIES_PATH = Path("data/youtube_search_queries.txt")
DEFAULT_JSON_OUTPUT = Path("data/youtube_api_recipes.json")
DEFAULT_CSV_OUTPUT = Path("data/youtube_api_recipes.csv")
DEFAULT_ENV_PATH = Path(".env")
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


def load_local_env(path: Path = DEFAULT_ENV_PATH) -> None:
    """Load simple KEY=value pairs from .env without printing secrets."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and key not in os.environ:
            os.environ[key] = value


def api_get(endpoint: str, params: dict[str, str | int]) -> dict:
    """Call YouTube Data API and return parsed JSON."""
    load_local_env()
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("YOUTUBE_API_KEY is not set. Export it or add it to .env.")

    query = urllib.parse.urlencode({**params, "key": api_key})
    url = f"{API_BASE}/{endpoint}?{query}"
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def read_queries(path: Path) -> list[str]:
    """Read non-empty search queries from text file."""
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def normalize_video_id(item: dict) -> str:
    """Extract videoId from a search result item."""
    item_id = item.get("id") or {}
    if isinstance(item_id, dict):
        return item_id.get("videoId") or ""
    return str(item_id)


def is_usable_search_item(item: dict) -> bool:
    """Reject playlists, summaries, and likely non-recipe videos."""
    video_id = normalize_video_id(item)
    snippet = item.get("snippet") or {}
    title = snippet.get("title") or ""
    if not video_id:
        return False
    return not any(word in title for word in EXCLUDED_TITLE_WORDS)


def search_videos(query: str, max_pages: int, sleep_seconds: float, search_duration: str) -> list[dict]:
    """Search videos for one query."""
    items = []
    page_token = ""
    for _ in range(max_pages):
        params = {
            "part": "snippet",
            "type": "video",
            "q": query,
            "maxResults": 50,
            "regionCode": "JP",
            "relevanceLanguage": "ja",
            "videoEmbeddable": "true",
            "safeSearch": "moderate",
        }
        if search_duration != "any":
            params["videoDuration"] = search_duration
        if page_token:
            params["pageToken"] = page_token

        payload = api_get("search", params)
        items.extend(item for item in payload.get("items", []) if is_usable_search_item(item))
        page_token = payload.get("nextPageToken") or ""
        if not page_token:
            break
        time.sleep(sleep_seconds)
    return items


def chunked(values: list[str], size: int) -> list[list[str]]:
    """Split values into chunks."""
    return [values[index : index + size] for index in range(0, len(values), size)]


def fetch_video_details(video_ids: list[str], sleep_seconds: float) -> dict[str, dict]:
    """Fetch video details for collected IDs."""
    details = {}
    for group in chunked(video_ids, 50):
        payload = api_get(
            "videos",
            {
                "part": "snippet,contentDetails,statistics,status",
                "id": ",".join(group),
                "maxResults": 50,
            },
        )
        for item in payload.get("items", []):
            details[item["id"]] = item
        time.sleep(sleep_seconds)
    return details


def parse_duration_seconds(duration: str) -> int:
    """Parse an ISO 8601 YouTube duration such as PT1M23S."""
    match = re.fullmatch(
        r"P(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?",
        duration or "",
    )
    if not match:
        return 0
    days = int(match.group("days") or 0)
    hours = int(match.group("hours") or 0)
    minutes = int(match.group("minutes") or 0)
    seconds = int(match.group("seconds") or 0)
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def is_likely_recipe_video(title: str, description: str) -> bool:
    """Keep complete recipe videos and reject eating-only or lifestyle videos."""
    text = f"{title}\n{description[:1200]}"
    if any(word in text for word in NON_RECIPE_TEXT_PATTERNS):
        return False
    return any(word in text for word in RECIPE_HINT_WORDS)


def is_accepted_detail(detail_item: dict | None, max_duration_seconds: int) -> bool:
    if not detail_item:
        return True

    status = detail_item.get("status") or {}
    if not status.get("embeddable", True):
        return False

    snippet = detail_item.get("snippet") or {}
    title = snippet.get("title") or ""
    description = snippet.get("description") or ""
    if any(word in title for word in EXCLUDED_TITLE_WORDS):
        return False
    if not is_likely_recipe_video(title, description):
        return False

    duration = ((detail_item.get("contentDetails") or {}).get("duration")) or ""
    seconds = parse_duration_seconds(duration)
    return not seconds or seconds <= max_duration_seconds


def build_record(search_item: dict, detail_item: dict | None = None) -> dict[str, str | int]:
    """Merge search and detail API payloads into one flat record."""
    video_id = normalize_video_id(search_item)
    snippet = (detail_item or search_item).get("snippet") or {}
    statistics = (detail_item or {}).get("statistics") or {}
    status = (detail_item or {}).get("status") or {}
    content_details = (detail_item or {}).get("contentDetails") or {}
    duration_seconds = parse_duration_seconds(content_details.get("duration") or "")
    thumbnails = snippet.get("thumbnails") or {}
    thumbnail = (
        thumbnails.get("maxres")
        or thumbnails.get("standard")
        or thumbnails.get("high")
        or thumbnails.get("medium")
        or thumbnails.get("default")
        or {}
    )

    return {
        "platform": "youtube",
        "external_id": video_id,
        "video_url": f"https://www.youtube.com/watch?v={video_id}",
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": snippet.get("title") or "",
        "channel": snippet.get("channelTitle") or "",
        "published_at": snippet.get("publishedAt") or "",
        "description": snippet.get("description") or "",
        "thumbnail_url": thumbnail.get("url") or "",
        "view_count": int(statistics.get("viewCount") or 0),
        "like_count": int(statistics.get("likeCount") or 0),
        "duration_seconds": duration_seconds,
        "is_short": bool(duration_seconds and duration_seconds <= 60) or "#shorts" in (snippet.get("title") or "").lower(),
        "embeddable": bool(status.get("embeddable", True)),
        "privacy_status": status.get("privacyStatus") or "",
    }


def write_json(path: Path, records: list[dict]) -> None:
    """Write records as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, records: list[dict]) -> None:
    """Write records as CSV."""
    if not records:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    preferred_fieldnames = [
        "platform",
        "external_id",
        "video_url",
        "video_id",
        "url",
        "title",
        "channel",
        "published_at",
        "description",
        "thumbnail_url",
        "view_count",
        "like_count",
        "duration_seconds",
        "is_short",
        "embeddable",
        "privacy_status",
    ]
    discovered_fieldnames = list(dict.fromkeys(key for record in records for key in record.keys()))
    fieldnames = [
        *[fieldname for fieldname in preferred_fieldnames if fieldname in discovered_fieldnames],
        *[fieldname for fieldname in discovered_fieldnames if fieldname not in preferred_fieldnames],
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def record_video_id(record: dict) -> str:
    """Extract a stable YouTube ID from a stored record."""
    return str(record.get("video_id") or record.get("external_id") or "")


def read_existing_records(path: Path) -> dict[str, dict]:
    """Load previously collected records so follow-up runs can fill only gaps."""
    if not path.exists():
        return {}

    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    if not isinstance(records, list):
        return {}

    return {
        video_id: record
        for record in records
        if isinstance(record, dict)
        for video_id in [record_video_id(record)]
        if video_id
    }


def collect(args: argparse.Namespace) -> list[dict]:
    """Collect search results and detail records."""
    queries = read_queries(Path(args.queries))
    existing_records_by_id = read_existing_records(Path(args.json_output)) if args.merge_existing else {}
    search_items_by_id = {}
    needed_count = max(0, args.target_count - len(existing_records_by_id))
    search_target_count = needed_count * args.candidate_multiplier

    if existing_records_by_id:
        print(f"Loaded {len(existing_records_by_id)} existing records from {args.json_output}")
    if needed_count == 0:
        return list(existing_records_by_id.values())[: args.target_count]

    for query_index, query in enumerate(queries, 1):
        if len(search_items_by_id) >= search_target_count:
            break
        print(f"[query {query_index}/{len(queries)}] {query}")
        try:
            items = search_videos(query, args.pages_per_query, args.sleep, args.search_duration)
        except urllib.error.HTTPError as error:
            print(f"Stopped API search after HTTP {error.code}. Saving records collected so far.")
            break
        except urllib.error.URLError as error:
            print(f"Stopped API search after network error: {error.reason}. Saving records collected so far.")
            break

        for item in items:
            video_id = normalize_video_id(item)
            if not video_id or video_id in existing_records_by_id:
                continue
            if video_id not in search_items_by_id:
                search_items_by_id[video_id] = item
            if len(search_items_by_id) >= search_target_count:
                break

    video_ids = list(search_items_by_id.keys())
    try:
        details = fetch_video_details(video_ids, args.sleep)
    except urllib.error.HTTPError as error:
        print(f"Skipped detail fetch after HTTP {error.code}. Keeping existing records only.")
        details = {}
    except urllib.error.URLError as error:
        print(f"Skipped detail fetch after network error: {error.reason}. Keeping existing records only.")
        details = {}

    new_records = [
        build_record(search_items_by_id[video_id], details.get(video_id))
        for video_id in video_ids
        if is_accepted_detail(details.get(video_id), args.max_duration_seconds)
    ]
    records_by_id = {**existing_records_by_id, **{record_video_id(record): record for record in new_records}}
    return list(records_by_id.values())[: args.target_count]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect recipe videos with YouTube Data API.")
    parser.add_argument("--target-count", type=int, default=1000)
    parser.add_argument("--queries", default=str(DEFAULT_QUERIES_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT))
    parser.add_argument("--pages-per-query", type=int, default=8)
    parser.add_argument("--sleep", type=float, default=0.1)
    parser.add_argument("--max-duration-seconds", type=int, default=300)
    parser.add_argument("--candidate-multiplier", type=int, default=3)
    parser.add_argument("--search-duration", choices=("any", "short", "medium", "long"), default="short")
    parser.add_argument("--merge-existing", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    records = collect(args)
    write_json(Path(args.json_output), records)
    write_csv(Path(args.csv_output), records)
    print(f"Saved {len(records)} records to {args.json_output} and {args.csv_output}")


if __name__ == "__main__":
    main()
