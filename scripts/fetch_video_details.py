import json
from pathlib import Path

from yt_dlp import YoutubeDL


def main():
    input_path = Path("data/youtube_candidates.json")
    output_path = Path("data/youtube_details.json")
    candidates = json.loads(input_path.read_text(encoding="utf-8"))

    options = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
        "extractor_args": {"youtube": {"lang": ["ja"]}},
    }

    details = []
    with YoutubeDL(options) as ydl:
        for index, candidate in enumerate(candidates, 1):
            try:
                info = ydl.extract_info(candidate["url"], download=False)
                details.append(
                    {
                        **candidate,
                        "title": info.get("title") or candidate.get("title"),
                        "creator": info.get("channel")
                        or info.get("uploader")
                        or candidate.get("creator"),
                        "duration_seconds": info.get("duration")
                        or candidate.get("duration_seconds"),
                        "description": info.get("description") or "",
                    }
                )
                print(f"[{index:02d}/{len(candidates)}] {candidate['target']}: ok")
            except Exception as error:
                details.append({**candidate, "detail_error": str(error)})
                print(f"[{index:02d}/{len(candidates)}] {candidate['target']}: ERROR {error}")

    output_path.write_text(
        json.dumps(details, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved {len(details)} details to {output_path}")


if __name__ == "__main__":
    main()
