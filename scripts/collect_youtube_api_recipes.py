"""Collect recipe videos with YouTube Data API and save JSON/CSV.

Set YOUTUBE_API_KEY before running:
    export YOUTUBE_API_KEY="..."
    python3 scripts/collect_youtube_api_recipes.py --target-count 1000
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path


API_BASE = "https://www.googleapis.com/youtube/v3"
DEFAULT_QUERIES_PATH = Path("data/youtube_search_queries.txt")
DEFAULT_JSON_OUTPUT = Path("data/youtube_api_recipes.json")
DEFAULT_CSV_OUTPUT = Path("data/youtube_api_recipes.csv")
EXCLUDED_TITLE_WORDS = ("まとめ", "ランキング", "献立", "作り置き", "総集編", "ライブ", "切り抜き")


def api_get(endpoint: str, params: dict[str, str | int]) -> dict:
    """Call YouTube Data API and return parsed JSON."""
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("YOUTUBE_API_KEY is not set.")

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


def search_videos(query: str, max_pages: int, sleep_seconds: float) -> list[dict]:
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


def build_record(search_item: dict, detail_item: dict | None = None) -> dict[str, str | int]:
    """Merge search and detail API payloads into one flat record."""
    video_id = normalize_video_id(search_item)
    snippet = (detail_item or search_item).get("snippet") or {}
    statistics = (detail_item or {}).get("statistics") or {}
    status = (detail_item or {}).get("status") or {}
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
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": snippet.get("title") or "",
        "channel": snippet.get("channelTitle") or "",
        "published_at": snippet.get("publishedAt") or "",
        "description": snippet.get("description") or "",
        "thumbnail_url": thumbnail.get("url") or "",
        "view_count": int(statistics.get("viewCount") or 0),
        "like_count": int(statistics.get("likeCount") or 0),
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
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)


def collect(args: argparse.Namespace) -> list[dict]:
    """Collect search results and detail records."""
    queries = read_queries(Path(args.queries))
    search_items_by_id = {}

    for query_index, query in enumerate(queries, 1):
        if len(search_items_by_id) >= args.target_count:
            break
        print(f"[query {query_index}/{len(queries)}] {query}")
        for item in search_videos(query, args.pages_per_query, args.sleep):
            video_id = normalize_video_id(item)
            if video_id not in search_items_by_id:
                search_items_by_id[video_id] = item
            if len(search_items_by_id) >= args.target_count:
                break

    video_ids = list(search_items_by_id.keys())[: args.target_count]
    details = fetch_video_details(video_ids, args.sleep)
    records = [
        build_record(search_items_by_id[video_id], details.get(video_id))
        for video_id in video_ids
        if not details.get(video_id) or details[video_id].get("status", {}).get("embeddable", True)
    ]
    return records[: args.target_count]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect recipe videos with YouTube Data API.")
    parser.add_argument("--target-count", type=int, default=1000)
    parser.add_argument("--queries", default=str(DEFAULT_QUERIES_PATH))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--csv-output", default=str(DEFAULT_CSV_OUTPUT))
    parser.add_argument("--pages-per-query", type=int, default=3)
    parser.add_argument("--sleep", type=float, default=0.1)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    records = collect(args)
    write_json(Path(args.json_output), records)
    write_csv(Path(args.csv_output), records)
    print(f"Saved {len(records)} records to {args.json_output} and {args.csv_output}")


if __name__ == "__main__":
    main()
