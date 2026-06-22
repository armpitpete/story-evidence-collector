"""Validate Proof Trail output files.

This is a local, file-based validator for Proof Trail v1 output.

It checks structure, required fields, reference links, evidence-grade risks,
human-review flags, and cautious wording. It does not fetch pages, crawl links,
call AI, judge truth, or prove accusations.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SOURCE_TYPES = {
    "official_record",
    "government_page",
    "parliament_record",
    "court_document",
    "manifesto",
    "speech",
    "interview",
    "news_article",
    "press_release",
    "social_post",
    "video",
    "audio",
    "transcript",
    "screenshot",
    "other",
}

EVIDENCE_GRADES = {"A", "B", "C", "D", "E"}
CONFIDENCE_LEVELS = {"low", "medium", "high"}

SERIOUS_WORDS = (
    "lie",
    "lied",
    "lying",
    "corrupt",
    "corruption",
    "fraud",
    "criminal",
    "illegal",
    "cover-up",
    "coverup",
    "scandal",
    "caught",
)

OVERCLAIM_PHRASES = (
    "this proves",
    "proves that",
    "no evidence exists",
    "they lied",
    "caught contradicting",
    "definitely proves",
    "undeniable proof",
)


@dataclass
class ValidationIssue:
    severity: str
    path: str
    message: str


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("top-level JSON value must be an object")

    return data


def find_json_records(folder: Path) -> list[tuple[Path, dict[str, Any]]]:
    records: list[tuple[Path, dict[str, Any]]] = []

    if not folder.exists():
        return records

    for path in sorted(folder.glob("*.json")):
        records.append((path, load_json(path)))

    return records


def as_bool(value: Any) -> bool:
    return value is True


def add_issue(
    issues: list[ValidationIssue],
    severity: str,
    path: Path | str,
    message: str,
) -> None:
    issues.append(ValidationIssue(severity=severity, path=str(path), message=message))


def text_contains_serious_word(*values: Any) -> bool:
    text = " ".join(str(value or "") for value in values).lower()
    return any(re.search(rf"\b{re.escape(word)}\b", text) for word in SERIOUS_WORDS)


def text_contains_overclaim(value: str) -> str | None:
    lower = value.lower()
    for phrase in OVERCLAIM_PHRASES:
        if phrase in lower:
            return phrase
    return None


def require_fields(
    issues: list[ValidationIssue],
    path: Path,
    record: dict[str, Any],
    fields: list[str],
) -> None:
    for field in fields:
        value = record.get(field)
        if value is None or value == "":
            add_issue(issues, "ERROR", path, f"missing required field: {field}")


def validate_sources(
    records: list[tuple[Path, dict[str, Any]]],
    issues: list[ValidationIssue],
) -> set[str]:
    source_ids: set[str] = set()

    for path, record in records:
        require_fields(
            issues,
            path,
            record,
            ["id", "title", "url", "source_type", "collected_at"],
        )

        source_id = str(record.get("id", "")).strip()
        if source_id:
            source_ids.add(source_id)

        source_type = str(record.get("source_type", "")).strip()
        if source_type and source_type not in SOURCE_TYPES:
            add_issue(issues, "ERROR", path, f"unknown source_type: {source_type}")

        if not record.get("archive_url") and not record.get("local_copy_path"):
            add_issue(
                issues,
                "WARNING",
                path,
                "source has no archive_url or local_copy_path; proof trail may be weaker",
            )

    return source_ids


def validate_claims(
    records: list[tuple[Path, dict[str, Any]]],
    source_ids: set[str],
    issues: list[ValidationIssue],
) -> set[str]:
    claim_ids: set[str] = set()

    for path, record in records:
        require_fields(
            issues,
            path,
            record,
            ["id", "source_id", "claim_text", "confidence", "human_checked"],
        )

        claim_id = str(record.get("id", "")).strip()
        if claim_id:
            claim_ids.add(claim_id)

        source_id = str(record.get("source_id", "")).strip()
        if source_id and source_id not in source_ids:
            add_issue(issues, "ERROR", path, f"unknown source_id reference: {source_id}")

        confidence = str(record.get("confidence", "")).strip()
        if confidence and confidence not in CONFIDENCE_LEVELS:
            add_issue(issues, "ERROR", path, f"unknown confidence level: {confidence}")

        if not record.get("date_claimed"):
            add_issue(issues, "WARNING", path, "claim has no date_claimed")

        if (
            text_contains_serious_word(
                record.get("claim_text"),
                record.get("plain_meaning"),
                record.get("position"),
                record.get("notes"),
            )
            and not as_bool(record.get("human_checked"))
        ):
            add_issue(
                issues,
                "WARNING",
                path,
                "serious wording appears in claim fields but human_checked is not true",
            )

    return claim_ids


def validate_evidence_items(
    records: list[tuple[Path, dict[str, Any]]],
    source_ids: set[str],
    claim_ids: set[str],
    issues: list[ValidationIssue],
) -> None:
    strong_evidence_by_claim: set[str] = set()

    for _path, record in records:
        claim_id = str(record.get("claim_id", "")).strip()
        grade = str(record.get("evidence_grade", "")).strip().upper()

        if claim_id and grade in {"A", "B", "C", "D"}:
            strong_evidence_by_claim.add(claim_id)

    for path, record in records:
        require_fields(
            issues,
            path,
            record,
            ["id", "claim_id", "source_id", "excerpt", "evidence_grade", "human_checked"],
        )

        claim_id = str(record.get("claim_id", "")).strip()
        source_id = str(record.get("source_id", "")).strip()
        grade = str(record.get("evidence_grade", "")).strip().upper()

        if claim_id and claim_id not in claim_ids:
            add_issue(issues, "ERROR", path, f"unknown claim_id reference: {claim_id}")

        if source_id and source_id not in source_ids:
            add_issue(issues, "ERROR", path, f"unknown source_id reference: {source_id}")

        if grade and grade not in EVIDENCE_GRADES:
            add_issue(issues, "ERROR", path, f"unknown evidence_grade: {grade}")

        if grade == "E" and claim_id not in strong_evidence_by_claim:
            add_issue(
                issues,
                "WARNING",
                path,
                "Grade E evidence is used without stronger A-D evidence for the same claim",
            )

        if grade == "E" and not as_bool(record.get("human_checked")):
            add_issue(
                issues,
                "WARNING",
                path,
                "Grade E evidence has not been human-checked",
            )


def validate_briefs(
    records: list[Path],
    issues: list[ValidationIssue],
) -> None:
    required_sections = (
        "what is proven",
        "what is interpretation",
        "what needs checking",
        "what must not be overstated",
        "human review",
    )

    for path in records:
        text = path.read_text(encoding="utf-8")
        lower = text.lower()

        for section in required_sections:
            if section not in lower:
                add_issue(issues, "WARNING", path, f"brief may be missing section: {section}")

        phrase = text_contains_overclaim(text)
        if phrase:
            add_issue(
                issues,
                "WARNING",
                path,
                f"brief may contain overclaiming phrase: {phrase}",
            )


def validate(evidence_dir: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    source_records = find_json_records(evidence_dir / "sources")
    claim_records = find_json_records(evidence_dir / "claims")
    evidence_item_records = find_json_records(evidence_dir / "evidence-items")
    brief_records = sorted((evidence_dir / "briefs").glob("*.md")) if (evidence_dir / "briefs").exists() else []

    if not source_records:
        add_issue(issues, "ERROR", evidence_dir / "sources", "no source JSON records found")
    if not claim_records:
        add_issue(issues, "ERROR", evidence_dir / "claims", "no claim JSON records found")
    if not evidence_item_records:
        add_issue(issues, "ERROR", evidence_dir / "evidence-items", "no evidence item JSON records found")
    if not brief_records:
        add_issue(issues, "ERROR", evidence_dir / "briefs", "no Markdown brief records found")

    source_ids = validate_sources(source_records, issues)
    claim_ids = validate_claims(claim_records, source_ids, issues)
    validate_evidence_items(evidence_item_records, source_ids, claim_ids, issues)
    validate_briefs(brief_records, issues)

    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Proof Trail v1 evidence files.")
    parser.add_argument(
        "--evidence-dir",
        default="evidence",
        help="Evidence output directory to validate. Default: evidence",
    )
    parser.add_argument(
        "--warnings-as-errors",
        action="store_true",
        help="Return a failing exit code when warnings are present.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    evidence_dir = Path(args.evidence_dir)

    issues = validate(evidence_dir)
    errors = [issue for issue in issues if issue.severity == "ERROR"]
    warnings = [issue for issue in issues if issue.severity == "WARNING"]

    print("Proof Trail validation")
    print("----------------------")
    print(f"Evidence directory: {evidence_dir}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")

    for issue in issues:
        print(f"{issue.severity}: {issue.path}: {issue.message}")

    if errors:
        print("VALIDATION FAILED")
        return 1

    if warnings:
        print("VALIDATION PASSED WITH WARNINGS")
        return 1 if args.warnings_as_errors else 0

    print("VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
