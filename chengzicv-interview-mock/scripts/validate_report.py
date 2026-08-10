#!/usr/bin/env python3
"""Validate v4 report structure and evidence references."""

import json
import sys
from pathlib import Path

from schema_subset import SchemaValidationError, validate_schema


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) != 3:
        fail("usage: validate_report.py <report.json> <evidence-pack.json>")

    report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    pack = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    schema_path = Path(__file__).resolve().parent.parent / "schemas" / "report.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        validate_schema(report, schema)
    except SchemaValidationError as error:
        fail(f"schema validation failed: {error}")
    quote_ids = {
        quote["quote_id"]
        for question in pack.get("questions", [])
        for quote in question.get("quotes", [])
    }

    if report.get("schema_version") != "v4":
        fail("schema_version must be v4")
    verdict = report.get("advance_verdict", {})
    if verdict.get("level") not in {"推进", "待定", "当前不建议推进"}:
        fail("invalid advance verdict")
    dimensions = report.get("dimension_diagnoses")
    if not isinstance(dimensions, list) or not 4 <= len(dimensions) <= 6:
        fail("dimension_diagnoses must contain 4-6 items")

    reference_groups = [verdict.get("evidence_refs", [])]
    for key in ("dimension_diagnoses", "strengths", "primary_risks"):
        for item in report.get(key, []):
            reference_groups.append(item.get("evidence_refs", []))
            if key == "dimension_diagnoses":
                sufficiency = item.get("evidence_sufficiency")
                score = item.get("score")
                if sufficiency == "insufficient" and score is not None:
                    fail(f"insufficient evidence must use null score for {item.get('dimension_id')}")
                if sufficiency != "insufficient" and not isinstance(score, int):
                    fail(f"non-insufficient evidence requires integer score for {item.get('dimension_id')}")
    for card in report.get("evidence_cards", []):
        reference_groups.append([card.get("quote_id")])

    for refs in reference_groups:
        for ref in refs:
            if ref not in quote_ids:
                fail(f"unknown evidence reference: {ref}")

    if len(report.get("retry_tasks", [])) != 3:
        fail("retry_tasks must contain exactly 3 items")
    if not report.get("disclaimer", "").strip():
        fail("disclaimer is required")
    print("report ok")


if __name__ == "__main__":
    main()
