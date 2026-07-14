#!/usr/bin/env python3
"""Regression tests for Complete MP Report v1 contract enforcement."""

from __future__ import annotations

import copy
import tempfile
from pathlib import Path
from typing import Callable

from generate_complete_mp_report import (
    ReportValidationError,
    load_json,
    validate_report,
    write_outputs,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = (
    ROOT
    / "fixtures"
    / "complete-mp-reports"
    / "jeremy-corbyn-fixture-v1.json"
)

EXPECTED_FILENAMES = {
    "corbyn-jeremy-full-profile.json",
    "corbyn-jeremy-full-profile.md",
    "corbyn-jeremy-source-register.md",
    "corbyn-jeremy-coverage-report.md",
    "corbyn-jeremy-human-review.md",
}


def read_outputs(folder: Path) -> dict[str, str]:
    return {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(folder.iterdir())
        if path.is_file()
    }


def section(report: dict, section_id: str) -> dict:
    return next(
        item for item in report["sections"] if item["section_id"] == section_id
    )


def expect_rejected(
    base_report: dict,
    mutate: Callable[[dict], None],
    message_fragment: str,
) -> None:
    candidate = copy.deepcopy(base_report)
    mutate(candidate)
    try:
        validate_report(candidate)
    except ReportValidationError as exc:
        assert message_fragment in str(exc), (
            f"Expected {message_fragment!r} in rejection, got: {exc}"
        )
    else:
        raise AssertionError(
            f"Expected report to be rejected with {message_fragment!r}."
        )


def add_grounded_interpretation(report: dict) -> None:
    report["interpretations"].append(
        {
            "interpretation_id": "interpretation-test-grounded",
            "section_id": "identity_and_parliamentary_career",
            "statement": "Synthetic grounded interpretation for contract testing.",
            "fact_ids": ["fact-fixture-member-id"],
            "claim_ids": [],
            "human_review_required": True,
            "approved_for_publication": False,
            "approved_by": None,
            "notes": "Test-only record.",
        }
    )
    section(report, "identity_and_parliamentary_career")[
        "interpretation_ids"
    ].append("interpretation-test-grounded")


def make_publishable(report: dict) -> None:
    approval_time = "2026-07-14T13:00:00Z"
    report["publication"].update(
        {
            "status": "publishable",
            "human_review_required": False,
            "public_output_authorised": True,
            "approved_by": "Merrin",
            "approved_at": approval_time,
        }
    )
    for gap in report["coverage_gaps"]:
        gap["status"] = "resolved"
        gap["blocks_publication"] = False
    for claim in report["claims"]:
        claim["status"] = "supported"
        claim["public_wording_allowed"] = True
    for interpretation in report["interpretations"]:
        interpretation["approved_for_publication"] = True
        interpretation["approved_by"] = "Merrin"
    report["review_decisions"].append(
        {
            "review_id": "review-publication-approval",
            "review_type": "publication",
            "status": "approved",
            "decision": "Approved for fixture contract testing only.",
            "reviewer": "Merrin",
            "reviewed_at": approval_time,
            "related_fact_ids": [],
            "related_claim_ids": [],
            "related_gap_ids": [],
            "notes": "Synthetic contract-test approval record.",
        }
    )


def make_authoritative_test_records(report: dict) -> None:
    report["subject"]["identity_status"] = "verified"
    report["subject"]["current_constituency"] = "Synthetic test constituency"
    report["subject"]["current_party"] = "Synthetic test party"
    for source in report["sources"]:
        source["source_type"] = "official_primary"
        source["authority_level"] = "primary"
        source["limitations"] = "Synthetic authoritative contract-test source."
    for fact in report["facts"]:
        fact["evidence_status"] = "verified"
        fact["confidence"] = "high"


def test_happy_path(report: dict) -> None:
    validate_report(report)
    assert report["publication"]["status"] == "not_ready"
    assert len(report["sections"]) == 13

    with (
        tempfile.TemporaryDirectory() as first_dir,
        tempfile.TemporaryDirectory() as second_dir,
    ):
        first = Path(first_dir)
        second = Path(second_dir)

        write_outputs(report, first)
        write_outputs(report, second)

        first_outputs = read_outputs(first)
        second_outputs = read_outputs(second)

        assert set(first_outputs) == EXPECTED_FILENAMES
        assert first_outputs == second_outputs
        assert (
            "# Complete MP Report — Corbyn, Jeremy"
            in first_outputs["corbyn-jeremy-full-profile.md"]
        )
        assert "not_ready" in first_outputs["corbyn-jeremy-human-review.md"]
        assert (
            "Historic vote coverage is incomplete"
            in first_outputs["corbyn-jeremy-coverage-report.md"]
        )


def test_safe_publishable_path(report: dict) -> None:
    candidate = copy.deepcopy(report)
    make_authoritative_test_records(candidate)
    add_grounded_interpretation(candidate)
    make_publishable(candidate)
    validate_report(candidate)
    assert candidate["publication"]["status"] == "publishable"
    assert candidate["subject"]["identity_status"] == "verified"


def test_negative_cases(report: dict) -> None:
    expect_rejected(
        report,
        lambda candidate: candidate.__setitem__("unexpected", True),
        "Schema validation failed",
    )

    def compact_date(candidate: dict) -> None:
        candidate["scope"]["as_of_date"] = "20260714"

    expect_rejected(report, compact_date, "not a valid date")

    def week_date(candidate: dict) -> None:
        candidate["scope"]["as_of_date"] = "2026-W29-2"

    expect_rejected(report, week_date, "not a valid date")

    def invalid_calendar_date(candidate: dict) -> None:
        candidate["scope"]["as_of_date"] = "2026-02-30"

    expect_rejected(report, invalid_calendar_date, "not a valid date")

    def missing_timezone(candidate: dict) -> None:
        candidate["generated_at"] = "2026-07-14T12:00:00"

    expect_rejected(report, missing_timezone, "not a valid date-time")

    def space_separated_datetime(candidate: dict) -> None:
        candidate["generated_at"] = "2026-07-14 12:00:00Z"

    expect_rejected(report, space_separated_datetime, "not a valid date-time")

    def duplicate_fact(candidate: dict) -> None:
        candidate["facts"].append(copy.deepcopy(candidate["facts"][0]))

    expect_rejected(report, duplicate_fact, "Duplicate fact ID")

    def unresolved_fact_source(candidate: dict) -> None:
        candidate["facts"][0]["source_ids"] = ["source-does-not-exist"]

    expect_rejected(report, unresolved_fact_source, "unresolved source_ids")

    def unresolved_identity_source(candidate: dict) -> None:
        candidate["subject"]["identity_source_ids"] = ["source-does-not-exist"]

    expect_rejected(
        report,
        unresolved_identity_source,
        "unresolved identity_source_ids",
    )

    def missing_identity_sources(candidate: dict) -> None:
        candidate["subject"]["identity_source_ids"] = []

    expect_rejected(
        report,
        missing_identity_sources,
        "identity_source_ids must contain at least one source ID",
    )

    def missing_canonical_section(candidate: dict) -> None:
        candidate["sections"].pop()

    expect_rejected(report, missing_canonical_section, "Schema validation failed")

    def ungrounded_claim(candidate: dict) -> None:
        candidate["claims"][0]["source_ids"] = []
        candidate["claims"][0]["fact_ids"] = []

    expect_rejected(
        report,
        ungrounded_claim,
        "must reference at least one source or fact",
    )

    def ungrounded_interpretation(candidate: dict) -> None:
        candidate["interpretations"].append(
            {
                "interpretation_id": "interpretation-test-ungrounded",
                "section_id": "public_positions_over_time",
                "statement": "Synthetic ungrounded interpretation.",
                "fact_ids": [],
                "claim_ids": [],
                "human_review_required": True,
                "approved_for_publication": False,
                "approved_by": None,
                "notes": "",
            }
        )
        section(candidate, "public_positions_over_time")[
            "interpretation_ids"
        ].append("interpretation-test-ungrounded")

    expect_rejected(
        report,
        ungrounded_interpretation,
        "must reference at least one fact or claim",
    )

    def orphan_fact(candidate: dict) -> None:
        section(candidate, "identity_and_parliamentary_career")["fact_ids"].remove(
            "fact-fixture-member-id"
        )

    expect_rejected(report, orphan_fact, "Orphan fact fact-fixture-member-id")

    def multiply_listed_fact(candidate: dict) -> None:
        section(candidate, "voting_record_and_coverage")["fact_ids"].append(
            "fact-fixture-member-id"
        )

    expect_rejected(
        report,
        multiply_listed_fact,
        "Multiply listed fact fact-fixture-member-id",
    )

    def cross_section_fact(candidate: dict) -> None:
        section(candidate, "identity_and_parliamentary_career")["fact_ids"].remove(
            "fact-fixture-member-id"
        )
        section(candidate, "voting_record_and_coverage")["fact_ids"].append(
            "fact-fixture-member-id"
        )

    expect_rejected(
        report,
        cross_section_fact,
        "Cross-section fact fact-fixture-member-id",
    )

    def unsafe_public_wording(candidate: dict) -> None:
        make_publishable(candidate)
        candidate["claims"][0]["public_wording_allowed"] = False

    expect_rejected(
        report,
        unsafe_public_wording,
        "claims not authorised for public wording",
    )

    def missing_traceable_approval(candidate: dict) -> None:
        make_publishable(candidate)
        candidate["review_decisions"] = [
            item
            for item in candidate["review_decisions"]
            if item["review_id"] != "review-publication-approval"
        ]

    expect_rejected(
        report,
        missing_traceable_approval,
        "lacks a traceable matching publication approval",
    )

    def mismatched_traceable_approval(candidate: dict) -> None:
        make_publishable(candidate)
        candidate["publication"]["approved_at"] = "2026-07-14T13:01:00Z"

    expect_rejected(
        report,
        mismatched_traceable_approval,
        "lacks a traceable matching publication approval",
    )

    def blocking_gap(candidate: dict) -> None:
        make_publishable(candidate)
        candidate["coverage_gaps"][0]["status"] = "open"
        candidate["coverage_gaps"][0]["blocks_publication"] = True

    expect_rejected(report, blocking_gap, "Publishable report has blocking gaps")

    def unsupported_claim(candidate: dict) -> None:
        make_publishable(candidate)
        candidate["claims"][0]["status"] = "unsupported"

    expect_rejected(
        report,
        unsupported_claim,
        "Publishable report has unsupported claims",
    )

    def unapproved_interpretation(candidate: dict) -> None:
        add_grounded_interpretation(candidate)
        make_publishable(candidate)
        candidate["interpretations"][0]["approved_for_publication"] = False
        candidate["interpretations"][0]["approved_by"] = None

    expect_rejected(
        report,
        unapproved_interpretation,
        "Publishable report has unapproved interpretations",
    )

    def invalid_public_relationship(candidate: dict) -> None:
        candidate["relationships"].append(
            {
                "relationship_id": "relationship-test-low-confidence",
                "section_id": "organisations_and_relationships",
                "subject": "Test subject",
                "object": "Test organisation",
                "relationship_type": "member_of",
                "date_from": None,
                "date_to": None,
                "source_ids": ["source-mp-query-fixture"],
                "confidence": "low",
                "public_chart": True,
                "neutral_label": "member of",
                "notes": "",
            }
        )
        section(candidate, "organisations_and_relationships")[
            "relationship_ids"
        ].append("relationship-test-low-confidence")

    expect_rejected(
        report,
        invalid_public_relationship,
        "Schema validation failed",
    )


def main() -> int:
    report = load_json(FIXTURE)
    test_happy_path(report)
    test_safe_publishable_path(report)
    test_negative_cases(report)
    print("PASS: Complete MP Report v1 contract enforcement")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
