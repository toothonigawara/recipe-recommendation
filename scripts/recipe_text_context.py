"""Utilities for separating reliable recipe text from noisy YouTube text."""

from __future__ import annotations

import re
from dataclasses import dataclass


RECIPE_SECTION_MARKERS = (
    "今回のレシピはこちら",
    "今回のレシピ",
    "材料はこちら",
    "材料",
    "レシピはこちら",
)
MATERIAL_SECTION_MARKERS = (
    "材料はこちら",
    "材料",
    "【材料】",
    "[材料]",
    "■材料",
    "▼材料",
    "●材料",
    "分量",
)
PROCESS_SECTION_MARKERS = (
    "作り方",
    "手順",
    "工程",
    "ポイント",
    "コツ",
    "詳しい作り方",
)
PROMO_SECTION_MARKERS = (
    "◆",
    "▼",
    "～～",
    "書籍のお知らせ",
    "チャンネル登録",
    "こちらもおすすめ",
    "関連動画",
    "おすすめ動画",
    "SNS",
    "Twitter",
    "Instagram",
    "TikTok",
    "Amazon",
    "楽天",
    "ホームページ",
    "グッズ販売",
    "STORE",
    "ダウンロードはこちら",
    "お仕事",
    "サブチャンネル",
)

HASHTAG_RE = re.compile(r"[#＃][^\s#＃]+")
URL_RE = re.compile(r"https?://\S+")


@dataclass(frozen=True)
class RecipeTextContext:
    title: str
    title_core: str
    title_hashtags: str
    intro: str
    materials: str
    hashtags: str

    @property
    def strong_text(self) -> str:
        return "\n".join(part for part in (self.title_core, self.materials) if part)

    @property
    def medium_text(self) -> str:
        return self.intro

    @property
    def weak_text(self) -> str:
        return "\n".join(part for part in (self.title_hashtags, self.hashtags) if part)

    @property
    def reliable_text(self) -> str:
        return "\n".join(part for part in (self.strong_text, self.medium_text) if part)

    @property
    def all_weighted_text(self) -> str:
        return "\n".join(part for part in (self.reliable_text, self.weak_text) if part)


def clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def strip_hashtags(value: str) -> str:
    return clean(HASHTAG_RE.sub(" ", value))


def extract_hashtags(value: str) -> str:
    return " ".join(tag.lstrip("#＃") for tag in HASHTAG_RE.findall(value))


def line_has_promo_marker(line: str) -> bool:
    if line_has_material_marker(line) or any(marker in line for marker in RECIPE_SECTION_MARKERS):
        return False
    return any(marker in line for marker in PROMO_SECTION_MARKERS)


def line_has_material_marker(line: str) -> bool:
    return any(marker in line for marker in MATERIAL_SECTION_MARKERS)


def line_has_process_marker(line: str) -> bool:
    return any(marker in line for marker in PROCESS_SECTION_MARKERS)


def relevant_lines(description: str) -> list[str]:
    lines = []
    for raw_line in (description or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if URL_RE.search(line):
            continue
        if line_has_promo_marker(line):
            break
        lines.append(line)
    return lines


def build_text_context(title: str | None, description: str | None) -> RecipeTextContext:
    title = clean(title)
    title_core = strip_hashtags(title)
    title_hashtags = extract_hashtags(title)
    lines = relevant_lines(description or "")

    hashtags = []
    intro_lines = []
    material_lines = []
    material_started = False

    for line in lines:
        hashtags.append(extract_hashtags(line))
        clean_line = strip_hashtags(line)
        if not clean_line:
            continue

        if line_has_material_marker(clean_line):
            material_started = True
            material_lines.append(clean_line)
            continue

        if material_started and line_has_process_marker(clean_line):
            material_started = False
            continue

        if material_started:
            material_lines.append(clean_line)
        elif len(intro_lines) < 8:
            intro_lines.append(clean_line)

    if material_lines:
        intro_lines = [
            line
            for line in intro_lines
            if not any(marker in line for marker in RECIPE_SECTION_MARKERS)
        ]

    return RecipeTextContext(
        title=title,
        title_core=title_core,
        title_hashtags=title_hashtags,
        intro="\n".join(intro_lines)[:800],
        materials="\n".join(material_lines)[:1200],
        hashtags=" ".join(tag for tag in hashtags if tag),
    )
