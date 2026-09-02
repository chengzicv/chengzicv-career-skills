#!/usr/bin/env python3
"""Internally audit recruiter-platform opening signals and chosen length limits."""

from __future__ import annotations

import argparse
import json
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
        "passed": bool(normalized)
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
