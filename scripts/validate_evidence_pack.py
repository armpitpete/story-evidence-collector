#!/usr/bin/env python3
"""Validate a TWIS evidence pack folder.

Validator v1 is intentionally small and stdlib-only.

It checks structure only:
- pack.json exists
- pack.json is valid JSON
- pack.json conforms to the manually enforced Manifest Schema v1 fields
- files listed in records exist
- files listed in outputs exist
- JSONL files parse line by line

It does not make editorial judgements.
It does not decide whether evidence is true.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SCHEMA_RELATIVE_PATH = Path("schemas/evidence-pack-manifest-v1.schema.json")

PACK_ID_PATTERN = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9]+(?:-[a-z0-9]+)*$"
)

ABSOLUTE_PATH_PATTERN = re.compile(r"^[A-Za-z]:\\|^/")

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

OPTIONAL_PACK_FIELDS = [
    "pack_schema_version",
    "notes",
]

ALLOWED_PACK_FIELDS = sorted(set(REQUIRED_PACK_FIELDS + OPTIONAL_PACK_FIELDS))

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

ALLOWED_RECORD_FIELDS = sorted(REQUIRED_RECORD_FIELDS)

REQUIRED_OUTPUT_FIELDS = [
    "final_brief",
    "evidence_summary",
    "contradiction_brief",
]

ALLOWED_OUTPUT_FIELDS = sorted(REQUIRED_OUTPUT_FIELDS)

STATUS_VALUES = {
    "draft",
    "active",
    "in_review",
    "reviewed",
    "archived",
}

EDITORIAL_RISK_VALUES = {
    "low",
    "medium",
    "high",
}

PUBLISHABILITY_VALUES = {
    "not_ready",
    "needs_review",
    "publishable",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except OSError as exc:
        raise ValueError(f"{path}: could not read JSON file: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")

    return data


def load_manifest_schema() -> dict[str, Any]:
    """Load the schema file this validator manually enforces.

    This is not a full JSON Schema implementation. It confirms that the schema
    file exists and is valid JSON, then the validator enforces the v1 fields
    directly using stdlib code.
    """

    schema_path = repo_root() / SCHEMA_RELATIVE_PATH
    return load_json(schema_path)


def require_fields(data: dict[str, Any], fields: list[str], label: str) -> list[str]:
    errors: list[str] = []

    for field in fields:
        if field not in data:
            errors.append(f"{label}: missing required field: {field}")

    return errors


def reject_extra_fields(
    data: dict[str, Any], allowed_fields: list[str], label: str
) -> list[str]:
    errors: list[str] = []
    allowed = set(allowed_fields)

    for field in sorted(data):
        if field not in allowed:
            errors.append(f"{label}: unexpected field: {field}")

    return errors


def require_string(data: dict[str, Any], field: str, label: str) -> list[str]:
    value = data.get(field)

    if not isinstance(value, str):
        return [f"{label}.{field}: must be a string"]

    if not value:
        return [f"{label}.{field}: must not be empty"]

    return []


def require_optional_string(data: dict[str, Any], field: str, label: str) -> list[str]:
    if field not in data:
        return []

    if not isinstance(data[field], str):
        return [f"{label}.{field}: must be a string"]

    return []


def require_const_string(
    data: dict[str, Any], field: str, expected: str, label: str
) -> list[str]:
    if field not in data:
        return []

    value = data[field]

    if not isinstance(value, str):
        return [f"{label}.{field}: must be a string"]

    if value != expected:
        return [f"{label}.{field}: must be {expected!r}"]

    return []


def require_boolean(data: dict[str, Any], field: str, label: str) -> list[str]:
    if not isinstance(data.get(field), bool):
        return [f"{label}.{field}: must be a boolean"]

    return []


def require_enum(
    data: dict[str, Any], field: str, allowed_values: set[str], label: str
) -> list[str]:
    value = data.get(field)

    if not isinstance(value, str):
        return [f"{label}.{field}: must be a string"]

    if value not in allowed_values:
        allowed = ", ".join(sorted(allowed_values))
        return [f"{label}.{field}: must be one of: {allowed}"]

    return []


def require_pack_id(data: dict[str, Any], field: str, label: str) -> list[str]:
    value = data.get(field)

    if not isinstance(value, str):
        return [f"{label}.{field}: must be a string"]

    if not value:
        return [f"{label}.{field}: must not be empty"]

    if not PACK_ID_PATTERN.match(value):
        return [
            f"{label}.{field}: must match YYYY-MM-DD-topic-name using lowercase letters, numbers, and hyphens"
        ]

    return []


def require_date_time(data: dict[str, Any], field: str, label: str) -> list[str]:
    value = data.get(field)

    if not isinstance(value, str):
        return [f"{label}.{field}: must be a string"]

    if not value:
        return [f"{label}.{field}: must not be empty"]

    if "T" not in value:
        return [f"{label}.{field}: must be a valid ISO date-time string"]

    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return [f"{label}.{field}: must be a valid ISO date-time string"]

    return []


def validate_schema_shape(manifest: dict[str, Any]) -> list[str]:
    """Manually enforce the current manifest schema without external packages."""

    errors: list[str] = []

    errors.extend(require_fields(manifest, REQUIRED_PACK_FIELDS, "pack.json"))
    errors.extend(reject_extra_fields(manifest, ALLOWED_PACK_FIELDS, "pack.json"))

    if "pack_schema_version" in manifest:
        errors.extend(require_const_string(manifest, "pack_schema_version", "1", "pack.json"))

    if "pack_id" in manifest:
        errors.extend(require_pack_id(manifest, "pack_id", "pack.json"))

    for field in ["title", "research_question", "scope"]:
        if field in manifest:
            errors.extend(require_string(manifest, field, "pack.json"))

    if "status" in manifest:
        errors.extend(require_enum(manifest, "status", STATUS_VALUES, "pack.json"))

    for field in ["created_at", "updated_at"]:
        if field in manifest:
            errors.extend(require_date_time(manifest, field, "pack.json"))

    if "editorial_risk" in manifest:
        errors.extend(
            require_enum(manifest, "editorial_risk", EDITORIAL_RISK_VALUES, "pack.json")
        )

    if "publishability" in manifest:
        errors.extend(
            require_enum(manifest, "publishability", PUBLISHABILITY_VALUES, "pack.json")
        )

    if "human_review_required" in manifest:
        errors.extend(require_boolean(manifest, "human_review_required", "pack.json"))

    errors.extend(require_optional_string(manifest, "notes", "pack.json"))

    records = manifest.get("records")
    if "records" in manifest:
        if not isinstance(records, dict):
            errors.append("pack.json.records: must be an object")
        else:
            errors.extend(require_fields(records, REQUIRED_RECORD_FIELDS, "pack.json.records"))
            errors.extend(
                reject_extra_fields(records, ALLOWED_RECORD_FIELDS, "pack.json.records")
            )

            for field in REQUIRED_RECORD_FIELDS:
                if field in records:
                    errors.extend(require_string(records, field, "pack.json.records"))

    outputs = manifest.get("outputs")
    if "outputs" in manifest:
        if not isinstance(outputs, dict):
            errors.append("pack.json.outputs: must be an object")
        else:
            errors.extend(require_fields(outputs, REQUIRED_OUTPUT_FIELDS, "pack.json.outputs"))
            errors.extend(
                reject_extra_fields(outputs, ALLOWED_OUTPUT_FIELDS, "pack.json.outputs")
            )

            for field in REQUIRED_OUTPUT_FIELDS:
                if field in outputs:
                    errors.extend(require_string(outputs, field, "pack.json.outputs"))

    return errors


def validate_jsonl(path: Path) -> list[str]:
    errors: list[str] = []

    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
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

    if Path(relative_path).is_absolute() or ABSOLUTE_PATH_PATTERN.match(relative_path):
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
        load_manifest_schema()
    except ValueError as exc:
        return [str(exc)]

    try:
        manifest = load_json(pack_json)
    except ValueError as exc:
        return [str(exc)]

    errors.extend(validate_schema_shape(manifest))

    records = manifest.get("records")
    if isinstance(records, dict):
        for field in REQUIRED_RECORD_FIELDS:
            if field in records:
                errors.extend(validate_path(pack_dir, records[field], f"records.{field}"))

    outputs = manifest.get("outputs")
    if isinstance(outputs, dict):
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
