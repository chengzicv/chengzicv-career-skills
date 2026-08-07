#!/usr/bin/env python3
"""Validate v4 Evidence Pack structure and exact quote provenance."""

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    Draft202012Validator = None


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) != 3:
        fail("usage: validate_evidence_pack.py <evidence-pack.json> <messages.json>")

    pack = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    messages_data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    if Draft202012Validator is None:
        fail("missing dependency: install scripts/requirements.txt")
    schema_path = Path(__file__).resolve().parent.parent / "schemas" / "evidence-pack.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(pack), key=lambda item: list(item.path))
    if errors:
        fail(f"schema validation failed: {errors[0].message}")
    messages = messages_data["messages"] if isinstance(messages_data, dict) else messages_data
    by_id = {item["message_id"]: item for item in messages}

    if pack.get("schema_version") != "v4":
        fail("schema_version must be v4")
    questions = pack.get("questions")
    if not isinstance(questions, list) or not 5 <= len(questions) <= 6:
        fail("questions must contain 5-6 items")

    quote_ids = set()
    for question in questions:
        for quote in question.get("quotes", []):
            quote_id = quote.get("quote_id")
            if not quote_id or quote_id in quote_ids:
                fail(f"invalid or duplicate quote_id: {quote_id}")
            quote_ids.add(quote_id)
            message_id = quote.get("source_message_id")
            if message_id not in by_id:
                fail(f"unknown source_message_id for {quote_id}: {message_id}")
            message = by_id[message_id]
            if message.get("role") != "user":
                fail(f"quote {quote_id} does not reference a user message")
            content = message.get("content", "")
            start, end = quote.get("start_char"), quote.get("end_char")
            if not isinstance(start, int) or not isinstance(end, int) or not 0 <= start < end <= len(content):
                fail(f"invalid character range for {quote_id}")
            if content[start:end] != quote.get("text"):
                fail(f"quote text mismatch for {quote_id}")

    for question in questions:
        for contradiction in question.get("contradictions", []):
            for ref in contradiction.get("evidence_refs", []):
                if ref not in quote_ids:
                    fail(f"unknown contradiction evidence_ref: {ref}")

    print("evidence pack ok")


if __name__ == "__main__":
    main()
