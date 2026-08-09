import json
import re
from pathlib import Path

from yt_dlp import YoutubeDL


TARGETS = [
    "牛丼",
    "豚丼",
    "カツ丼",
    "天津飯",
    "オムライス",
    "タコライス",
    "ビビンバ",
    "炊き込みご飯",
    "ドライカレー",
    "キーマカレー",
    "生姜焼き",
    "豚キムチ",
    "回鍋肉",
    "酢豚",
    "鶏の照り焼き",
    "唐揚げ",
    "チキン南蛮",
    "油淋鶏",
    "ロールキャベツ",
    "ビーフシチュー",
    "クリームシチュー",
    "ローストビーフ",
    "鶏むね肉のレンジ蒸し",
    "手羽元のさっぱり煮",
    "鮭のムニエル",
    "鮭のホイル焼き",
    "ぶりの照り焼き",
    "さばの味噌煮",
    "あじの南蛮漬け",
    "魚の煮付け",
    "エビチリ",
    "アクアパッツァ",
    "ツナアボカド丼",
    "まぐろ漬け丼",
    "ラタトゥイユ",
    "ミネストローネ",
    "ポトフ",
    "ピーマンの肉詰め",
    "なすの味噌炒め",
    "かぼちゃの煮物",
    "きんぴらごぼう",
    "ほうれん草のごま和え",
    "もやしナムル",
    "ポテトサラダ",
    "コールスロー",
    "無限キャベツ",
    "筑前煮",
    "揚げ出し豆腐",
    "豆腐ハンバーグ",
    "ゴーヤチャンプルー",
    "だし巻き卵",
    "茶碗蒸し",
    "卵サンド",
    "ナポリタン",
    "ペペロンチーノ",
    "ミートソースパスタ",
    "ボンゴレ",
    "焼きうどん",
    "きつねうどん",
    "カレーうどん",
    "ざるそば",
    "担々麺",
    "冷やし中華",
    "そうめんチャンプルー",
    "フォー",
    "豚汁",
    "コーンスープ",
    "クラムチャウダー",
    "わかめスープ",
    "オニオンスープ",
    "グラタン",
    "コロッケ",
    "天ぷら",
    "お好み焼き",
    "たこ焼き",
    "フレンチトースト",
    "ホットサンド",
    "カプレーゼ",
    "きゅうりの塩昆布和え",
    "サバ缶サラダ",
    "冷奴アレンジ",
]

EXCLUDED_TITLE_WORDS = ("選", "まとめ", "献立", "作り置き", "ランキング")


def normalize(value):
    return re.sub(r"[\s　【】\[\]（）()・]", "", value or "").lower()


def choose_entry(target, entries):
    target_normalized = normalize(target)
    usable = [
        entry
        for entry in entries
        if entry
        and entry.get("id")
        and not any(word in (entry.get("title") or "") for word in EXCLUDED_TITLE_WORDS)
        and (entry.get("duration") or 0) <= 1800
    ]

    exact = [
        entry
        for entry in usable
        if target_normalized in normalize(entry.get("title"))
    ]
    return (exact or usable or entries or [None])[0]


def main():
    assert len(TARGETS) == 81, f"Expected 81 targets, got {len(TARGETS)}"

    output_path = Path("data/youtube_candidates.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results = []

    options = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
        "playlistend": 6,
        "extractor_args": {"youtube": {"lang": ["ja"]}},
    }

    with YoutubeDL(options) as ydl:
        for index, target in enumerate(TARGETS, 1):
            query = f"ytsearch6:{target} 作り方 レシピ"
            try:
                search_result = ydl.extract_info(query, download=False)
                entries = search_result.get("entries") or []
                selected = choose_entry(target, entries)
                if not selected:
                    raise RuntimeError("No usable search result")
                results.append(
                    {
                        "target": target,
                        "video_id": selected.get("id"),
                        "url": f"https://www.youtube.com/watch?v={selected.get('id')}",
                        "title": selected.get("title"),
                        "creator": selected.get("channel") or selected.get("uploader"),
                        "duration_seconds": selected.get("duration"),
                        "view_count": selected.get("view_count"),
                    }
                )
                print(f"[{index:02d}/81] {target}: {selected.get('title')}")
            except Exception as error:
                results.append({"target": target, "error": str(error)})
                print(f"[{index:02d}/81] {target}: ERROR {error}")

    output_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved {len(results)} candidates to {output_path}")


if __name__ == "__main__":
    main()
