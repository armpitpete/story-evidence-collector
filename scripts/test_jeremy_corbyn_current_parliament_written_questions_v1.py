#!/usr/bin/env python3
"""Regression proof for Jeremy Corbyn current-Parliament written questions v1."""

from __future__ import annotations

import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from generate_complete_mp_report import load_json, validate_report, write_outputs

ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = (
    ROOT
    / "research"
    / "complete-mp-reports"
    / "jeremy-corbyn"
    / "current-parliament-written-questions-v1.json"
)
FIXTURE_PATH = (
    ROOT
    / "fixtures"
    / "complete-mp-reports"
    / "jeremy-corbyn-fixture-v1.json"
)

MEMBERS_SOURCE_ID = (
    "source-uk-parliament-members-api-corbyn-"
    "written-questions-2026-07-20"
)
DETAIL_SOURCE_ID = (
    "source-uk-parliament-questions-api-corbyn-"
    "written-question-details-2026-07-20"
)
CAPTURE_SHA256 = (
    "af77384595f9bc8898e3a4812984bd3b3d95d84e1cf175bef386ed2f62ccec4b"
)
CAPTURE_SIZE = 2380198
EXPECTED_PAGE_ITEM_COUNTS = [20] * 12 + [11]
EXPECTED_YEAR_COUNTS = {"2024": 14, "2025": 15, "2026": 61}
EXPECTED_ANSWERING_BODY_COUNTS = {
    "Cabinet Office": 3,
    "Department for Business and Trade": 4,
    "Department for Culture, Media and Sport": 2,
    "Department for Education": 2,
    "Department for Environment, Food and Rural Affairs": 6,
    "Department for Transport": 5,
    "Department for Work and Pensions": 2,
    "Department of Health and Social Care": 6,
    "Foreign, Commonwealth and Development Office": 19,
    "Home Office": 3,
    "Ministry of Defence": 34,
    "Ministry of Housing, Communities and Local Government": 3,
    "Ministry of Justice": 1,
}
EXPECTED_OUTPUTS = {
    "corbyn-jeremy-full-profile.json",
    "corbyn-jeremy-full-profile.md",
    "corbyn-jeremy-source-register.md",
    "corbyn-jeremy-coverage-report.md",
    "corbyn-jeremy-human-review.md",
}


def load_packet() -> dict:
    value = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def by_id(records: list[dict], key: str) -> dict:
    result = {item[key]: item for item in records}
    assert len(result) == len(records), f"Duplicate {key}"
    return result


def section(report: dict, section_id: str) -> dict:
    return next(
        item
        for item in report["sections"]
        if item["section_id"] == section_id
    )


def canonical_sha256(value: object) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def question_value(record: dict) -> dict:
    value = record["detail_payload"]["value"]
    assert isinstance(value, dict)
    return value


def index_value(record: dict) -> dict:
    value = record["index_item"]["value"]
    assert isinstance(value, dict)
    return value


def test_packet_capture() -> None:
    packet = load_packet()

    assert packet["packet_id"] == (
        "jeremy-corbyn-current-parliament-written-questions-v1"
    )
    assert packet["section_id"] == "speeches_and_questions"
    assert packet["subject"] == {
        "official_name": "Jeremy Corbyn",
        "uk_parliament_member_id": "185",
    }
    assert packet["captured_at"] == "2026-07-20T20:00:41Z"

    scope = packet["scope"]
    assert scope["house"] == "House of Commons"
    assert scope["record_type"] == "written_questions"
    assert scope["tabled_from"] == "2024-07-04"
    assert scope["tabled_to"] == "2026-07-20"
    assert scope["spoken_contributions_included"] is False
    assert scope["oral_questions_included"] is False
    assert scope["written_statements_included"] is False
    assert scope["early_day_motions_included"] is False

    capture_source = packet["capture_source"]
    assert capture_source["byte_length"] == CAPTURE_SIZE
    assert capture_source["sha256"] == CAPTURE_SHA256
    assert capture_source["original_result"] == "diagnostic_stop"
    assert "askingMemberId" in capture_source["original_parser_issue"]
    assert "No official record was re-requested" in capture_source[
        "repair_basis"
    ]

    members_contract = packet["official_api_contracts"][
        "members_api_swagger"
    ]
    assert members_contract["resolved_path"] == (
        "/api/Members/{id}/WrittenQuestions"
    )
    assert members_contract["parameter_names"] == ["id", "page"]

    questions_contract = packet["official_api_contracts"][
        "questions_api_swagger"
    ]
    assert questions_contract["resolved_path"] == (
        "/api/writtenquestions/questions/{date}/{uin}"
    )

    members_capture = packet["members_api_capture"]
    assert members_capture["reported_total_results"] == 251
    assert members_capture["page_count"] == 13
    assert members_capture["pagination_mode"] == "page"
    assert [item["item_count"] for item in members_capture["pages"]] == (
        EXPECTED_PAGE_ITEM_COUNTS
    )
    assert all(
        item["payload_total_results"] == 251
        for item in members_capture["pages"]
    )
    assert all(
        len(item["sha256"]) == 64
        for item in members_capture["pages"]
    )

    checks = packet["capture_checks"]
    assert checks["members_api_reported_total"] == 251
    assert checks["members_api_page_count"] == 13
    assert checks["members_api_page_item_counts"] == (
        EXPECTED_PAGE_ITEM_COUNTS
    )
    assert checks["members_api_unique_question_id_count"] == 251
    assert checks["members_api_unique_date_uin_count"] == 251
    assert checks["members_api_all_asking_member_id_185"] is True
    assert checks["members_api_all_house_commons"] is True
    assert checks["in_scope_question_count"] == 90
    assert checks["in_scope_unique_question_id_count"] == 90
    assert checks["in_scope_unique_date_uin_count"] == 90
    assert checks["detail_direct_asking_member_id_185_count"] == 90
    assert checks["detail_nested_asking_member_null_count"] == 90
    assert checks["detail_index_exact_match_count"] == 90
    assert checks["answered_count"] == 89
    assert checks["unanswered_count"] == 1
    assert checks["unanswered_question_ids"] == [1919112]
    assert checks["unanswered_uins"] == ["12037"]
    assert checks["withdrawn_count"] == 0
    assert checks["named_day_count"] == 86
    assert checks["member_interest_recorded_count"] == 27
    assert checks["holding_answer_count"] == 1
    assert checks["correction_count"] == 0
    assert checks["attachment_count_total"] == 0
    assert checks["tabled_date_coverage"] == {
        "from": "2024-07-18",
        "to": "2026-07-01",
    }
    assert checks["tabled_year_counts"] == EXPECTED_YEAR_COUNTS
    assert checks["answering_body_counts"] == (
        EXPECTED_ANSWERING_BODY_COUNTS
    )

    index = packet["index_reconciliation"]
    assert len(index) == 251
    assert len({item["question_id"] for item in index}) == 251
    assert len(
        {(item["tabled_date"], item["uin"]) for item in index}
    ) == 251
    assert all(item["asking_member_id"] == 185 for item in index)
    assert all(item["house"] == 1 for item in index)
    assert sum(item["in_scope"] for item in index) == 90

    records = packet["records"]
    assert len(records) == 90
    records_by_id = by_id(records, "question_id")
    assert len(records_by_id) == 90
    assert len(
        {(item["tabled_date"], item["uin"]) for item in records}
    ) == 90

    detail_values: list[dict] = []
    for record in records:
        assert record["index_item_canonical_sha256"] == canonical_sha256(
            record["index_item"]
        )
        assert (
            record["detail_payload_canonical_sha256"]
            == canonical_sha256(record["detail_payload"])
        )

        index_item = index_value(record)
        detail = question_value(record)
        detail_values.append(detail)

        assert detail["id"] == record["question_id"]
        assert detail["id"] == index_item["id"]
        assert str(detail["uin"]) == record["uin"]
        assert str(detail["uin"]) == str(index_item["uin"])
        assert detail["dateTabled"][:10] == record["tabled_date"]
        assert index_item["dateTabled"][:10] == record["tabled_date"]
        assert detail["askingMemberId"] == 185
        assert index_item["askingMemberId"] == 185
        assert detail["askingMember"] is None
        assert detail["house"] == "Commons"
        assert index_item["house"] == 1
        assert all(record["cross_checks"].values())

    assert Counter(
        item["dateTabled"][:4] for item in detail_values
    ) == Counter(EXPECTED_YEAR_COUNTS)
    assert Counter(
        item["answeringBodyName"] for item in detail_values
    ) == Counter(EXPECTED_ANSWERING_BODY_COUNTS)
    assert sum(item["dateAnswered"] is not None for item in detail_values) == 89
    assert sum(item["dateAnswered"] is None for item in detail_values) == 1
    assert sum(item["isWithdrawn"] is True for item in detail_values) == 0
    assert sum(item["isNamedDay"] is True for item in detail_values) == 86
    assert sum(
        item["memberHasInterest"] is True for item in detail_values
    ) == 27
    assert sum(
        item["answerIsHolding"] is True for item in detail_values
    ) == 1
    assert sum(
        item["answerIsCorrection"] is True for item in detail_values
    ) == 0
    assert sum(item["attachmentCount"] or 0 for item in detail_values) == 0

    unanswered = records_by_id[1919112]
    unanswered_value = question_value(unanswered)
    assert unanswered["uin"] == "12037"
    assert unanswered_value["dateAnswered"] is None
    assert unanswered_value["answerText"] is None
    assert unanswered_value["answeringMemberId"] is None

    sources = by_id(packet["sources"], "source_id")
    assert set(sources) == {MEMBERS_SOURCE_ID, DETAIL_SOURCE_ID}

    members_source = sources[MEMBERS_SOURCE_ID]
    assert members_source["publisher"] == "UK Parliament"
    assert members_source["source_type"] == "parliamentary_record"
    assert members_source["authority_level"] == "primary"
    members_url = urlparse(members_source["url"])
    assert members_url.scheme == "https"
    assert members_url.netloc == "members-api.parliament.uk"

    detail_source = sources[DETAIL_SOURCE_ID]
    assert detail_source["publisher"] == "UK Parliament"
    assert detail_source["source_type"] == "parliamentary_record"
    assert detail_source["authority_level"] == "primary"
    detail_url = urlparse(detail_source["url"])
    assert detail_url.scheme == "https"
    assert detail_url.netloc == "questions-statements-api.parliament.uk"


def test_fixture_integration() -> None:
    packet = load_packet()
    report = load_json(FIXTURE_PATH)
    validate_report(report)

    packet_sources = by_id(packet["sources"], "source_id")
    packet_facts = by_id(packet["facts"], "fact_id")
    packet_gaps = by_id(packet["coverage_gaps"], "gap_id")

    report_sources = by_id(report["sources"], "source_id")
    report_facts = by_id(report["facts"], "fact_id")
    report_gaps = by_id(report["coverage_gaps"], "gap_id")

    expected_fact_ids = [
        f"fact-written-question-{record['question_id']}"
        for record in packet["records"]
    ]
    assert len(expected_fact_ids) == 90
    assert list(packet_facts) == expected_fact_ids

    speeches = section(report, "speeches_and_questions")
    assert speeches["status"] == "partial"
    section_fact_ids = speeches["fact_ids"]
    assert section_fact_ids[: len(expected_fact_ids)] == expected_fact_ids
    assert [
        fact_id
        for fact_id in section_fact_ids
        if fact_id.startswith("fact-written-question-")
    ] == expected_fact_ids
    assert speeches["claim_ids"] == []
    assert speeches["interpretation_ids"] == []
    assert speeches["relationship_ids"] == []
    assert speeches["gap_ids"] == [
        "gap-speeches-questions-current-parliament-scope"
    ]

    for source_id, source in packet_sources.items():
        assert source == report_sources[source_id]

    for fact_id, fact in packet_facts.items():
        assert fact == report_facts[fact_id]
        assert fact["section_id"] == "speeches_and_questions"
        assert fact["fact_type"] == "question"
        assert fact["source_ids"] == [
            MEMBERS_SOURCE_ID,
            DETAIL_SOURCE_ID,
        ]
        assert fact["confidence"] == "high"
        assert fact["evidence_status"] == "verified"
        assert "No topic classification" in fact["notes"]

    unanswered_fact = packet_facts["fact-written-question-1919112"]
    assert unanswered_fact["date"] == "2026-06-23"
    assert "UIN 12037" in unanswered_fact["statement"]
    assert "No answer date or answer text" in unanswered_fact["statement"]

    assert set(packet_gaps) == {
        "gap-speeches-questions-current-parliament-scope"
    }
    packet_gap = packet_gaps[
        "gap-speeches-questions-current-parliament-scope"
    ]
    shared_gap = report_gaps[
        "gap-speeches-questions-current-parliament-scope"
    ]
    assert packet_gap["section_id"] == shared_gap["section_id"]
    assert packet_gap["status"] == shared_gap["status"] == "open"
    assert packet_gap["blocks_publication"] is True
    assert shared_gap["blocks_publication"] is True
    shared_gap_text = " ".join(
        str(shared_gap.get(field, ""))
        for field in ("summary", "next_action", "notes")
    )
    for required_limit in (
        "written questions",
        "oral questions",
        "written statements",
        "Early Day Motions",
    ):
        assert required_limit.casefold() in shared_gap_text.casefold()
    assert "gap-speeches-questions" not in report_gaps

    assert not any(
        item["section_id"] == "speeches_and_questions"
        for item in report["claims"]
    )
    assert not any(
        item["section_id"] == "speeches_and_questions"
        for item in report["interpretations"]
    )
    assert not any(
        item["section_id"] == "speeches_and_questions"
        for item in report["relationships"]
    )

    assert report["publication"]["status"] == "not_ready"
    assert report["publication"]["human_review_required"] is True
    assert report["publication"]["public_output_authorised"] is False


def test_deterministic_generation() -> None:
    report = load_json(FIXTURE_PATH)
    validate_report(report)

    with (
        tempfile.TemporaryDirectory() as first_dir,
        tempfile.TemporaryDirectory() as second_dir,
    ):
        first = Path(first_dir)
        second = Path(second_dir)
        write_outputs(report, first)
        write_outputs(report, second)

        first_outputs = {
            path.name: path.read_bytes()
            for path in sorted(first.iterdir())
            if path.is_file()
        }
        second_outputs = {
            path.name: path.read_bytes()
            for path in sorted(second.iterdir())
            if path.is_file()
        }

        assert set(first_outputs) == EXPECTED_OUTPUTS
        assert first_outputs == second_outputs

        profile = first_outputs[
            "corbyn-jeremy-full-profile.md"
        ].decode("utf-8")
        source_register = first_outputs[
            "corbyn-jeremy-source-register.md"
        ].decode("utf-8")
        coverage = first_outputs[
            "corbyn-jeremy-coverage-report.md"
        ].decode("utf-8")

        for uin in [
            "14770",
            "128658",
            "12037",
            "69740",
            "590",
        ]:
            assert f"UIN {uin}" in profile

        assert MEMBERS_SOURCE_ID in source_register
        assert DETAIL_SOURCE_ID in source_register
        assert (
            "gap-speeches-questions-current-parliament-scope"
            in coverage
        )


def main() -> int:
    test_packet_capture()
    test_fixture_integration()
    test_deterministic_generation()
    print(
        "PASS - Jeremy Corbyn current-Parliament written questions baseline v1"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
