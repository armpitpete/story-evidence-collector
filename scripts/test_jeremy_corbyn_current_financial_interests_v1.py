#!/usr/bin/env python3
"""Regression proof for Jeremy Corbyn current financial interests v1."""

from __future__ import annotations

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
    / "current-financial-interests-v1.json"
)
FIXTURE_PATH = (
    ROOT
    / "fixtures"
    / "complete-mp-reports"
    / "jeremy-corbyn-fixture-v1.json"
)

OFFICIAL_SOURCE_IDS = {
    "source-uk-parliament-registered-interests-current",
    "source-uk-parliament-register-publications-2026-07-13",
}
ENTRY_SOURCE_ID = "source-uk-parliament-registered-interests-current"
FACT_IDS = [
    f"fact-financial-interest-{index:03d}" for index in range(1, 30)
]
ENTRY_IDS = [
    f"financial-interest-{index:03d}" for index in range(1, 30)
]
EXPECTED_CATEGORY_COUNTS = {
    "3. Gifts, benefits and hospitality from UK sources": 13,
    "4. Visits outside the UK": 12,
    "8. Miscellaneous": 4,
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


def by_id(records: list[dict], key: str) -> dict[str, dict]:
    result = {item[key]: item for item in records}
    assert len(result) == len(records), f"Duplicate {key}"
    return result


def section(report: dict, section_id: str) -> dict:
    return next(item for item in report["sections"] if item["section_id"] == section_id)


def field_map(fields: list[dict]) -> dict[str, str]:
    result = {item["label"]: item["value"] for item in fields}
    assert len(result) == len(fields), "Duplicate displayed field label"
    assert all(result.values()), "Empty displayed field value"
    return result


def test_packet_capture() -> None:
    packet = load_packet()

    assert packet["section_id"] == "financial_interests"
    assert packet["subject"]["parliament_member_id"] == "185"
    assert packet["captured_at"] == "2026-07-20T15:53:04Z"

    snapshot = packet["register_snapshot"]
    assert snapshot["publication_date"] == "2026-07-13"
    assert snapshot["displayed_result_count"] == 29
    assert snapshot["page_count"] == 2
    assert [page["captured_entry_count"] for page in snapshot["pages"]] == [20, 9]
    assert sum(page["captured_entry_count"] for page in snapshot["pages"]) == 29
    assert snapshot["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert "twelve months" in snapshot["retention_notice"]

    entries = packet["entries"]
    assert [entry["entry_id"] for entry in entries] == ENTRY_IDS
    assert len(entries) == snapshot["displayed_result_count"]
    assert Counter(entry["page"] for entry in entries) == {1: 20, 2: 9}
    assert Counter(entry["category"] for entry in entries) == EXPECTED_CATEGORY_COUNTS
    assert all("rectification" not in entry for entry in entries)

    donor_names: list[str] = []
    for entry in entries:
        assert entry["page"] in {1, 2}
        field_map(entry["fields"])
        if "donors" in entry:
            ordinals = [donor["ordinal"] for donor in entry["donors"]]
            assert ordinals == list(range(1, len(ordinals) + 1))
            for donor in entry["donors"]:
                donor_fields = field_map(donor["fields"])
                donor_names.append(donor_fields["Name of donor"])
        else:
            fields = field_map(entry["fields"])
            if "Name of donor" in fields:
                donor_names.append(fields["Name of donor"])

    assert "Peace and Justice Project" in donor_names
    assert "The Peace and Justice Project" in donor_names
    assert "Pece and Justice Project" in donor_names
    assert len(set(ENTRY_IDS)) == 29

    south_africa = entries[20]
    assert south_africa["entry_id"] == "financial-interest-021"
    assert len(south_africa["donors"]) == 3
    assert "Address of donor" not in field_map(south_africa["donors"][0]["fields"])
    assert "Address of donor" not in field_map(south_africa["donors"][1]["fields"])

    sources = by_id(packet["sources"], "source_id")
    assert set(sources) == OFFICIAL_SOURCE_IDS
    for source in sources.values():
        assert source["publisher"] == "UK Parliament"
        assert source["authority_level"] == "primary"
        assert source["source_type"] == "parliamentary_record"
        parsed = urlparse(source["url"])
        assert parsed.scheme == "https"
        assert parsed.netloc == "members.parliament.uk"
        assert source["capture_date"] == "2026-07-20"
    assert sources[ENTRY_SOURCE_ID]["publication_date"] == "2026-07-13"


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

    assert list(packet_facts) == FACT_IDS
    assert len(packet_facts) == packet["register_snapshot"]["displayed_result_count"]

    financial_section = section(report, "financial_interests")
    assert financial_section["status"] == "partial"
    assert financial_section["fact_ids"] == FACT_IDS
    assert financial_section["claim_ids"] == []
    assert financial_section["interpretation_ids"] == []
    assert financial_section["relationship_ids"] == []
    assert financial_section["gap_ids"] == [
        "gap-financial-interests-history-retention"
    ]

    for source_id, source in packet_sources.items():
        assert source == report_sources[source_id]

    for index, fact_id in enumerate(FACT_IDS):
        fact = packet_facts[fact_id]
        assert fact == report_facts[fact_id]
        assert fact["section_id"] == "financial_interests"
        assert fact["fact_type"] == "interest"
        assert fact["confidence"] == "high"
        assert fact["evidence_status"] == "verified"
        assert fact["source_ids"] == [ENTRY_SOURCE_ID]
        assert ENTRY_IDS[index] in fact["notes"]

    report_financial_fact_ids = [
        fact_id
        for fact_id, fact in report_facts.items()
        if fact["section_id"] == "financial_interests"
    ]
    assert report_financial_fact_ids == FACT_IDS

    assert not any(
        fact["fact_type"] in {
            "donation",
            "employment",
            "company",
            "relationship_context",
            "position",
        }
        for fact in packet_facts.values()
    )

    assert set(packet_gaps) == {"gap-financial-interests-history-retention"}
    assert packet_gaps["gap-financial-interests-history-retention"] == report_gaps[
        "gap-financial-interests-history-retention"
    ]
    assert "gap-financial-interests" not in report_gaps
    assert report_gaps["gap-financial-interests-history-retention"]["status"] == "open"
    assert (
        report_gaps["gap-financial-interests-history-retention"][
            "blocks_publication"
        ]
        is True
    )

    assert report["publication"]["status"] == "not_ready"
    assert report["publication"]["human_review_required"] is True
    assert report["publication"]["public_output_authorised"] is False
    assert report["claims"] and len(report["claims"]) == 1
    assert report["interpretations"] == []
    assert report["relationships"] == []
    assert len(report["review_decisions"]) == 1


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

        assert "Estimated value £63.79" in profile
        assert "Pece and Justice Project" in profile
        assert "South Africa and Namibia" in profile
        assert "Unpaid Director of Your Party UK Ltd" in profile
        for source_id in OFFICIAL_SOURCE_IDS:
            assert source_id in source_register
        assert "twelve-month retention display" in coverage


def main() -> int:
    test_packet_capture()
    test_fixture_integration()
    test_deterministic_generation()
    print("PASS — Jeremy Corbyn current financial interests baseline v1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
