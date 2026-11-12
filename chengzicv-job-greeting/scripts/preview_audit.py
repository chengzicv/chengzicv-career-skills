#!/usr/bin/env python3
"""Internally audit recruiter-platform opening signals and chosen length limits."""

from __future__ import annotations

import argparse
import json
import re
import sys


FORBIDDEN_OPENINGS = (
    "您好",
    "你好",
    "我是",
    "看到贵司岗位",
    "看到你们在招",
    "对贵公司感兴趣",
    "想应聘",
)

# 文风提示用的词表：只提示，不影响 passed。
FORMAL_WORDS = ("主导", "负责", "现任", "具备", "熟悉", "降至", "完成", "对接", "落地", "累计", "其中")
ORAL_WORDS = ("哦", "~", "～", "吧", "呢", "呀", "啦", "想了解了解", "都是我")
SELF_EVAL_WORDS = ("具备", "熟悉", "擅长", "精通", "能力强", "非常感兴趣", "经验丰富")
CJK = r"[一-鿿]"
LATIN = r"[A-Za-z]"
URL = re.compile(r"(https?://\S+|[\w.-]+\.(com|cn|io|net|org)(/\S*)?)")
LONG_SENTENCE = 45


def style_hints(text: str) -> list[str]:
    """返回文风提示：语气混用、数字格式、中英文间距、自评词、句长。"""
    hints: list[str] = []
    body = URL.sub("", text)

    formal = sum(body.count(w) for w in FORMAL_WORDS)
    # 句末单个波浪号是允许的软化写法（发给 HR 的默认结尾），不算口语混用。
    checked = body.rstrip()
    if checked.endswith(("~", "～")) and checked.count("~") + checked.count("～") == 1:
        checked = checked[:-1]
    oral = [w for w in ORAL_WORDS if w in checked]
    if formal >= 2 and oral:
        hints.append(f"书面正文里混了口语词：{'、'.join(oral)}，全篇保持一种语气")

    loose_numbers = re.findall(r"\d+(?:\.\d+)?\s*[wWkK](?![A-Za-z])|\d[\d,]*\s+\+|\d+\s*/\s*\d+", body)
    if loose_numbers:
        hints.append(f"数字写法像随手记：{'、'.join(loose_numbers)}，改成“15 万元”“第 3 名 / 共 92 支”这类完整写法")

    spaced = len(re.findall(f"{CJK} +{LATIN}|{LATIN} +{CJK}", body))
    tight = len(re.findall(f"{CJK}{LATIN}|{LATIN}{CJK}", body))
    if spaced and tight:
        hints.append(f"中英文之间的空格时有时无（有空格 {spaced} 处、无空格 {tight} 处），统一一种")

    self_eval = [w for w in SELF_EVAL_WORDS if w in body]
    if len(self_eval) >= 2:
        hints.append(f"自评词偏多：{'、'.join(self_eval)}，能换成动作或结果就换")

    sentences = [s for s in re.split(r"[。！？!?]", body) if s.strip()]
    if sentences:
        avg = sum(len(re.sub(r"\s", "", s)) for s in sentences) / len(sentences)
        if avg > LONG_SENTENCE:
            hints.append(f"平均句长约 {avg:.0f} 字，读的人要换好几口气，考虑拆句或拆成短消息气泡")

    return hints


def audit(text: str, preview_length: int, max_length: int) -> dict[str, object]:
    normalized = text.strip()
    preview = normalized[:preview_length]
    forbidden = next(
        (item for item in FORBIDDEN_OPENINGS if normalized.startswith(item)), None
    )
    return {
        "text": normalized,
        "preview": preview,
        "preview_length": len(preview),
        "character_count": len(normalized),
        "max_length": max_length,
        "within_limit": len(normalized) <= max_length,
        "forbidden_opening": forbidden,
        "style_hints": style_hints(normalized),
        "passed":bool(normalized)
        and len(preview) == min(preview_length, len(normalized))
        and len(normalized) <= max_length
        and forbidden is None,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check preview text, total Unicode characters, and weak openings."
    )
    parser.add_argument(
        "--text",
        action="append",
        help="Greeting to audit. Repeat for multiple greetings; stdin is used if omitted.",
    )
    parser.add_argument("--preview-length", type=int, default=15)
    parser.add_argument("--max-length", type=int, default=120)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.preview_length <= 0 or args.max_length <= 0:
        raise SystemExit("preview and maximum lengths must be positive")

    texts = args.text if args.text else [line for line in sys.stdin.read().splitlines() if line]
    if not texts:
        raise SystemExit("provide --text or at least one non-empty stdin line")

    results = [audit(text, args.preview_length, args.max_length) for text in texts]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if all(item["passed"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
