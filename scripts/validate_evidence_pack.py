#!/usr/bin/env python3
"""Validate a TWIS evidence pack folder.

Validator v1 is intentionally small.

It checks structure only:
- pack.json exists
- pack.json is valid JSON
- required manifest fields exist
- files listed in records exist
- files listed in outputs exist
- JSONL files parse line by line

It does not make editorial judgements.
It does not decide whether evidence is true.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_PACK_FIELDS = [
    "pack_id",
    "title",
    "status",
    "created_at",
    "updated_at",
    "research_question",
    "scope",
    "editorial_risk",
    "publishability",
    "human_review_required",
    "records",
    "outputs",
]

REQUIRED_RECORD_FIELDS = [
    "source_records",
    "source_authority_map",
    "claim_records",
    "evidence_items",
    "search_diary",
    "negative_evidence_log",
    "public_record_timeline",
    "denial_checks",
    "human_review",
]

REQUIRED_OUTPUT_FIELDS = [
    "final_brief",
    "evidence_summary",
    "contradiction_brief",
]


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")

    return data


def require_fields(data: dict[str, Any], fields: list[str], label: str) -> list[str]:
    errors: list[str] = []

    for field in fields:
        if field not in data:
            errors.append(f"{label}: missing required field: {field}")

    return errors


def validate_jsonl(path: Path) -> list[str]:
    errors: list[str] = []

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [f"{path}: could not read file: {exc}"]

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue

        try:
            json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{line_number}: invalid JSONL line: {exc}")

    return errors


def validate_path(pack_dir: Path, relative_path: str, label: str) -> list[str]:
    errors: list[str] = []

    if not isinstance(relative_path, str) or not relative_path.strip():
        return [f"{label}: path must be a non-empty string"]

    if Path(relative_path).is_absolute():
        return [f"{label}: path must be relative, got absolute path: {relative_path}"]

    target = pack_dir / relative_path

    if not target.exists():
        errors.append(f"{label}: missing file: {relative_path}")
        return errors

    if target.suffix == ".jsonl":
        errors.extend(validate_jsonl(target))

    return errors


def validate_pack(pack_dir: Path) -> list[str]:
    errors: list[str] = []

    pack_json = pack_dir / "pack.json"

    if not pack_json.exists():
        return [f"{pack_dir}: missing pack.json"]

    try:
        manifest = load_json(pack_json)
    except ValueError as exc:
        return [str(exc)]

    errors.extend(require_fields(manifest, REQUIRED_PACK_FIELDS, "pack.json"))

    records = manifest.get("records")
    if not isinstance(records, dict):
        errors.append("pack.json: records must be an object")
    else:
        errors.extend(require_fields(records, REQUIRED_RECORD_FIELDS, "pack.json.records"))

        for field in REQUIRED_RECORD_FIELDS:
            if field in records:
                errors.extend(validate_path(pack_dir, records[field], f"records.{field}"))

    outputs = manifest.get("outputs")
    if not isinstance(outputs, dict):
        errors.append("pack.json: outputs must be an object")
    else:
        errors.extend(require_fields(outputs, REQUIRED_OUTPUT_FIELDS, "pack.json.outputs"))

        for field in REQUIRED_OUTPUT_FIELDS:
            if field in outputs:
                errors.extend(validate_path(pack_dir, outputs[field], f"outputs.{field}"))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a TWIS evidence pack folder.")
    parser.add_argument("pack_dir", help="Path to the evidence pack folder")
    args = parser.parse_args()

    pack_dir = Path(args.pack_dir)

    if not pack_dir.exists():
        print(f"ERROR: pack folder does not exist: {pack_dir}", file=sys.stderr)
        return 1

    if not pack_dir.is_dir():
        print(f"ERROR: pack path is not a folder: {pack_dir}", file=sys.stderr)
        return 1

    errors = validate_pack(pack_dir)

    if errors:
        print("Evidence pack validation failed.")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Evidence pack validation passed.")
    print(f"Pack folder: {pack_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
