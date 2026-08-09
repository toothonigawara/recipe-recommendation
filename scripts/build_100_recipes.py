#!/usr/bin/env python3
import argparse
import csv
import json
import re
from pathlib import Path


SELECTED = [
    ("bEDibR0DVfg", "名古屋風スパイシーチキン"),
    ("ZXr7rYsL3nA", "カリッじゅわやみつきチキン"),
    ("oNX6IDwPFkw", "ネギ塩チキン"),
    ("oDee3Kv78-8", "甘辛ごまチキン"),
    ("QYbWnB1xD_4", "鶏むね肉の甘酢マヨチキン"),
    ("hF3F9oDX5BY", "鶏もも肉の旨だれ焼き"),
    ("uFMgxC8_tR0", "照り焼きチキン"),
    ("NyxRyLWfx5k", "ヤンニョムチキン"),
    ("S2inUyE9Nus", "チキンのクリーム煮"),
    ("7n5bwx7vPmw", "鶏の照り焼き"),
    ("M3sKIXEPJOs", "サバの照り焼き"),
    ("a2DcPy93zBc", "激うま鮭焼き"),
    ("rL_uMJY4Nrw", "焼きサバの南蛮漬け"),
    ("VOawcyhJC5c", "サーモンタルタル"),
    ("rYlz6MFeqbM", "鮭のレモンバター醤油"),
    ("EwkJVzvTI3w", "たらの甘酢あんかけ"),
    ("h2Sz2EUubkk", "アクアパッツァ"),
    ("1kZWrpttJEY", "白身魚の甘酢あんかけ"),
    ("v4INrfr2FjY", "豆腐とネギのうま出汁あんかけ"),
    ("_JYNaqzpwq4", "テリマヨ豆腐ステーキ"),
    ("ElfAVvMxmtA", "豆腐ステーキ"),
    ("hk4B0Ik5124", "もちもちチーズ豆腐"),
    ("3r3yZTTVkkQ", "豆腐キムチチヂミ"),
    ("DMJzWV6PTbA", "夢中漬け豆腐"),
    ("t41Et_oMqSY", "豆腐と卵のレンジ蒸し"),
    ("oeLusRF0YCw", "炒り豆腐"),
    ("XP2cz6hpgB4", "ニラ玉焼き"),
    ("pHM5aZJUOzg", "トマトときゅうりのツナ和え"),
    ("MN5DEKDtqyc", "なすの甘酢炒め"),
    ("bkW5Ia1bkxY", "塩だれキャベツ"),
    ("yBZTyMFHylw", "レタスのチョレギサラダ"),
    ("PYv4aW43FD4", "ピーマンと卵の炒め物"),
    ("a2OPvuBLajk", "にんじんガレット"),
    ("ujf82gdZfXU", "大根ステーキ"),
    ("QzsXY_PZrvQ", "蒸しキャベツのうまだれ"),
    ("Fui3boODPwM", "小松菜とちくわの旨塩ごま和え"),
    ("Dr6Rwh98Ocw", "豚バラつけ麺"),
    ("P5JjCw5zRS4", "ネギ豚つけそうめん"),
    ("zAB_N68rNbQ", "やみつきそうめん"),
    ("xe7pCfHAY6c", "時短油うどん"),
    ("t6TzMJVfaXw", "時短うどん"),
    ("mRdpfuiUIGg", "焼きそば麺のさっぱり冷麺"),
    ("sMKjoyUDm6c", "麻婆うどん"),
    ("Ii4qil63EgY", "かき玉うどん"),
    ("VyRjh3CAuV4", "豚じゃが炒め"),
    ("63pmDfTDJ0I", "チーズ煮込みハンバーグ"),
    ("tZ13rhI8iu0", "生姜焼き"),
    ("50_nURL62nM", "肉豆腐"),
    ("5fDke9I_PVQ", "肉巻きキャベツ"),
    ("TgIlxarViz8", "豚こま丸め焼き"),
    ("m0yXIgLS6bI", "じゃがいもとひき肉のチーズ焼き"),
    ("b60tx4lSSQ8", "肉野菜炒め"),
    ("t-m4Bqofzmk", "豚こま油淋鶏"),
    ("Tl_ebKQEuVA", "豚バラ白菜"),
    ("hUYiUW4503I", "豚のネギ塩炒め"),
    ("UP2qvbhbuuU", "豚バラとキャベツのフライパン蒸し"),
    ("AAB6D1iWjEw", "ふわふわ親子丼"),
    ("pxgNTZOvXFk", "簡単ビビンバ丼"),
    ("z37K6f4GvNQ", "豚バラ丼"),
    ("mO-9aQFdABI", "中華丼"),
    ("Hex5f0Uwgjc", "スタミナ丼"),
    ("dRlJUFQKl0U", "簡単豚丼"),
    ("9dsSxnAZ3jc", "漬けサーモン丼"),
    ("ZyJ60JRI_zo", "簡単牛丼"),
    ("Txm4e2I6NxE", "キャベツと卵の中華スープ"),
    ("Nyb7R7I3EOU", "野菜だけスープ"),
    ("fpamp1L7WaI", "旨辛春雨スープ"),
    ("TsDynf2dxJQ", "白菜とえのきの卵スープ"),
    ("J1XNvXH2Kuo", "野菜ちゃんぽんスープ"),
    ("NrayMe1GQeA", "丸ごとオニオンスープ"),
    ("CS1b74u9FOY", "レタススープ"),
    ("YxaIiYNIp3A", "野菜コンソメスープ"),
    ("0nMGyoPukJk", "だし焼きたまご"),
    ("UZNWfksoKhg", "キャベたま焼き"),
    ("nUBggQGwq-M", "レンチンオムライス"),
    ("9YAQWNafUVg", "悪魔のたまご丼"),
    ("iuDCG6Gtkg0", "5分卵チャーハン"),
    ("Xsic_by8jsY", "卵だけチャーハン"),
    ("BXOqmSIBxEI", "冷やしうどん"),
    ("rTRgwAs1E38", "塩だれきゅうり"),
    ("1ZhJrV3x6Pw", "ガスパチョ"),
]


TAG_WORDS = {
    "beef": ["牛肉", "牛こま", "牛バラ", "牛丼"],
    "pork": ["豚肉", "豚こま", "豚バラ", "ひき肉", "挽肉", "ハンバーグ", "生姜焼き"],
    "chicken": ["鶏肉", "鶏もも", "鶏むね", "チキン", "親子丼"],
    "minced_meat": ["ひき肉", "挽肉", "ハンバーグ", "そぼろ"],
    "bacon": ["ベーコン"],
    "salmon": ["鮭", "サーモン"],
    "mackerel": ["サバ", "鯖"],
    "whitefish": ["白身魚", "たら", "タラ"],
    "canned_tuna": ["ツナ"],
    "cabbage": ["キャベツ"],
    "cucumber": ["きゅうり", "キュウリ"],
    "potato": ["じゃがいも", "じゃが芋", "豚じゃが"],
    "onion": ["玉ねぎ", "玉葱", "オニオン"],
    "tomato": ["トマト", "ガスパチョ"],
    "eggplant": ["なす", "茄子"],
    "nira": ["ニラ", "にら"],
    "carrot": ["にんじん", "人参"],
    "green_onion": ["長ネギ", "長ねぎ", "ネギ", "ねぎ"],
    "napa_cabbage": ["白菜"],
    "bell_pepper": ["ピーマン"],
    "lettuce": ["レタス"],
    "enoki": ["えのき", "エノキ"],
    "komatsuna": ["小松菜"],
    "daikon": ["大根"],
    "egg": ["卵", "たまご", "玉子", "親子丼", "オムライス"],
    "tofu": ["豆腐"],
    "chikuwa": ["ちくわ"],
    "harusame": ["春雨"],
    "ginger": ["生姜", "しょうが"],
    "garlic": ["にんにく", "ニンニク", "ガーリック"],
    "rice": ["ご飯", "ごはん", "米", "丼", "チャーハン", "オムライス"],
    "udon": ["うどん"],
    "somen": ["そうめん", "素麺"],
    "noodles": ["中華麺", "つけ麺", "冷麺", "ちゃんぽん"],
    "yakisoba_noodles": ["焼きそば麺"],
    "pasta": ["パスタ", "スパゲティ"],
    "cheese": ["チーズ"],
    "butter": ["バター"],
}


FALLBACK_INGREDIENTS = {
    "鶏": "鶏肉、長ネギ、しょうゆ、酒、砂糖",
    "チキン": "鶏肉、しょうゆ、酒、香味調味料",
    "サバ": "サバ、しょうゆ、みりん、酒",
    "鮭": "鮭、塩、しょうゆ、油",
    "サーモン": "サーモン、玉ねぎ、調味料",
    "白身魚": "白身魚、野菜、調味料",
    "たら": "たら、野菜、甘酢だれ",
    "豆腐": "豆腐、薬味、調味料",
    "キャベツ": "キャベツ、調味料",
    "きゅうり": "きゅうり、塩、ごま油",
    "なす": "なす、油、しょうゆ、酢",
    "レタス": "レタス、調味料",
    "ピーマン": "ピーマン、卵、調味料",
    "にんじん": "にんじん、粉類、チーズ",
    "大根": "大根、バター、しょうゆ",
    "小松菜": "小松菜、ちくわ、調味料",
    "うどん": "うどん、だし、薬味、調味料",
    "そうめん": "そうめん、つゆ、薬味",
    "つけ麺": "中華麺、豚肉、つけだれ",
    "冷麺": "麺、野菜、冷たいスープ",
    "豚": "豚肉、野菜、しょうゆ、酒",
    "ハンバーグ": "合びき肉、玉ねぎ、チーズ、調味料",
    "肉豆腐": "豚肉、豆腐、長ネギ、しょうゆ",
    "親子丼": "鶏肉、卵、玉ねぎ、ご飯",
    "ビビンバ": "ひき肉、野菜、卵、ご飯",
    "中華丼": "肉、白菜、にんじん、ご飯",
    "牛丼": "牛肉、玉ねぎ、ご飯、しょうゆ",
    "スープ": "野菜、だし、調味料",
    "たまご": "卵、だし、調味料",
    "卵": "卵、ご飯、調味料",
    "ガスパチョ": "トマト、きゅうり、玉ねぎ、オリーブオイル",
}


def parse_player_response(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"ytInitialPlayerResponse\s*=\s*(\{.*?\});", text)
    if not match:
        raise ValueError(f"ytInitialPlayerResponse not found: {path}")
    return json.loads(match.group(1))["videoDetails"]


def clean_materials(description, menu):
    if description:
        markers = ["■材料", "【材料", "＜材料", "〈材料", "材料（", "材料 "]
        start = next((description.find(marker) for marker in markers if marker in description), -1)
        if start >= 0:
            block = description[start:]
            block = re.split(r"\n(?:■|【|＜|〈)?(?:作り方|手順|ポイント|詳しいレシピ|#)", block, maxsplit=1)[0]
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            block = "\n".join(lines[:24])
            if len(block) >= 12:
                return block[:1200]

    for keyword, value in FALLBACK_INGREDIENTS.items():
        if keyword in menu:
            return value
    return f"{menu}に必要な主材料と基本調味料"


def detailed_tags(menu, materials):
    text = f"{menu}\n{materials}"
    tags = [tag for tag, words in TAG_WORDS.items() if any(word in text for word in words)]
    return tags or ["other"]


def broad_tags(tags):
    meat = {"beef", "pork", "chicken", "minced_meat", "ham", "bacon"}
    fish = {"salmon", "mackerel", "whitefish", "canned_tuna"}
    soy = {"tofu", "soybean", "natto", "atsuage", "aburaage"}
    vegetable = {
        "cabbage", "cucumber", "potato", "onion", "tomato", "eggplant",
        "nira", "carrot", "green_onion", "napa_cabbage", "bell_pepper",
        "lettuce", "enoki", "komatsuna", "daikon",
    }
    result = []
    if meat.intersection(tags):
        result.append("meat")
    if fish.intersection(tags):
        result.append("fish")
    if soy.intersection(tags):
        result.append("soy")
    if vegetable.intersection(tags):
        result.append("vegetable")
    if not result or set(tags) - meat - fish - soy - vegetable:
        result.append("other")
    return result


def cooking_time(title, menu):
    match = re.search(r"(\d{1,2})\s*分", title)
    minutes = int(match.group(1)) if match else None
    if minutes is None:
        if any(word in menu for word in ["サラダ", "和え", "冷奴", "きゅうり", "タルタル"]):
            minutes = 8
        elif any(word in menu for word in ["煮込み", "南蛮漬け", "アクアパッツァ"]):
            minutes = 25
        else:
            minutes = 15
    category = "easy" if minutes <= 15 else "normal" if minutes <= 30 else "slow"
    return minutes, category


def cooking_method(menu, title):
    text = f"{menu} {title}"
    if any(word in text for word in ["サラダ", "和え", "タルタル", "漬けサーモン", "ガスパチョ", "塩だれきゅうり"]):
        return "和える"
    if any(word in text for word in ["レンジ", "レンチン"]):
        return "電子レンジ"
    if any(word in text for word in ["スープ", "煮込み", "肉豆腐", "牛丼", "親子丼", "中華丼"]):
        return "煮る"
    if any(word in text for word in ["うどん", "そうめん", "つけ麺", "冷麺"]):
        return "茹でる"
    if any(word in text for word in ["蒸し"]):
        return "蒸す"
    if any(word in text for word in ["炒め", "チャーハン", "生姜焼き", "ガレット"]):
        return "炒める"
    return "焼く"


def taste(menu):
    if any(word in menu for word in ["サラダ", "ガスパチョ", "塩だれきゅうり", "冷やし", "蒸し", "野菜だけ"]):
        return "light"
    if any(word in menu for word in ["甘辛", "マヨ", "ヤンニョム", "チーズ", "スタミナ", "油淋", "照り焼き", "ハンバーグ", "牛丼", "豚丼"]):
        return "rich"
    if any(word in menu for word in ["スープ", "豆腐", "甘酢", "うどん", "そうめん"]):
        return "semi-light"
    return "semi-rich"


def temperature(menu):
    return "cold" if any(word in menu for word in ["冷やし", "冷麺", "サラダ", "タルタル", "ガスパチョ", "塩だれきゅうり", "漬けサーモン"]) else "warm"


def load_existing(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-csv", required=True, type=Path)
    parser.add_argument("--watch-dir", required=True, type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--output-js", required=True, type=Path)
    parser.add_argument("--output-metadata", required=True, type=Path)
    args = parser.parse_args()

    existing = load_existing(args.source_csv)
    existing_ids = {
        match.group(1)
        for row in existing
        if (match := re.search(r"(?:shorts/|v=)([A-Za-z0-9_-]{11})", row["動画URL"]))
    }

    metadata = []
    recipes = []
    csv_rows = []
    for video_id, menu in SELECTED:
        if video_id in existing_ids:
            raise ValueError(f"Duplicate existing video: {video_id}")
        details = parse_player_response(args.watch_dir / f"{video_id}.html")
        title = details["title"]
        author = details["author"].strip()
        description = details.get("shortDescription", "")
        materials = clean_materials(description, menu)
        tags = detailed_tags(menu, materials)
        broad = broad_tags(tags)
        minutes, time_category = cooking_time(title, menu)
        method = cooking_method(menu, title)
        taste_category = taste(menu)
        temp = temperature(menu)
        no_heat = temp == "cold" and method == "和える"
        knife = not any(word in title for word in ["包丁不要", "包丁なし"])
        oil = 1 if no_heat else 2 if method in {"煮る", "茹でる", "電子レンジ", "蒸す"} else 3
        if taste_category == "rich":
            oil = min(5, oil + 1)
        effort = 1 if minutes <= 8 else 2 if minutes <= 15 else 3
        dishes = 1 if method in {"和える", "電子レンジ"} else 2
        feature = f"{minutes}分目安・{method}・{author}の実在YouTube動画"
        style = "短尺動画・手順を視覚的に確認しやすい"

        metadata.append({
            "videoId": video_id,
            "title": title,
            "author": author,
            "description": description,
            "lengthSeconds": int(details.get("lengthSeconds", 0)),
        })
        recipes.append({
            "title": menu,
            "url": f"https://www.youtube.com/shorts/{video_id}",
            "creator": author,
            "style": style,
            "taste": taste_category,
            "time": time_category,
            "temperature": temp,
            "ingredients": broad,
            "oil": oil,
            "effort": effort,
            "dishes": dishes,
            "steps": max(2, effort + 1),
            "knife": knife,
            "heat": not no_heat,
            "method": method,
            "detailedIngredients": tags,
            "rawIngredients": re.sub(r"\s+", " ", materials)[:240],
            "description": feature,
        })
        csv_rows.append({
            "メニュー": menu,
            "動画URL": f"https://www.youtube.com/shorts/{video_id}",
            "投稿者": author,
            "時間": f"{minutes}分",
            "食材": materials,
            "味（これをどう表現するか）": taste_category,
            "油感（油の量）": str(oil),
            "調理方法": method,
            "材料": str(max(1, min(5, len(tags)))),
            "投稿者の傾向": style,
            "特徴": feature,
            "その他": "YouTube公開情報から収集",
        })

    if len(existing) + len(csv_rows) != 100:
        raise ValueError(f"Expected 100 records, got {len(existing) + len(csv_rows)}")

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(existing[0].keys())
    with args.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing)
        writer.writerows(csv_rows)

    args.output_js.write_text(
        "window.EXTRA_RECIPES = " + json.dumps(recipes, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    args.output_metadata.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generated {args.output_csv} ({len(existing) + len(csv_rows)} recipes)")
    print(f"Generated {args.output_js} ({len(recipes)} extra recipes)")


if __name__ == "__main__":
    main()
