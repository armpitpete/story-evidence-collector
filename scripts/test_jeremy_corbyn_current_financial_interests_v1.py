#!/usr/bin/env python3
"""Regression proof for Jeremy Corbyn current financial interests baseline v1."""

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
EXPECTED_OUTPUTS = {
    "corbyn-jeremy-full-profile.json",
    "corbyn-jeremy-full-profile.md",
    "corbyn-jeremy-source-register.md",
    "corbyn-jeremy-coverage-report.md",
    "corbyn-jeremy-human-review.md",
}
OFFICIAL_SOURCE_IDS = {
    "source-uk-parliament-registered-interests-page-1",
    "source-uk-parliament-registered-interests-page-2",
    "source-uk-parliament-register-publication-2026-07-13",
}
ENTRY_SOURCE_IDS = {
    "source-uk-parliament-registered-interests-page-1",
    "source-uk-parliament-registered-interests-page-2",
}
EXPECTED_CATEGORY_COUNTS = {3: 13, 4: 12, 8: 4}


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


def test_packet_and_fixture() -> None:
    packet = load_packet()
    report = load_json(FIXTURE_PATH)
    validate_report(report)

    assert packet["section_id"] == "financial_interests"
    assert packet["subject"] == {
        "official_name": "Jeremy Corbyn",
        "repository_display_name": "Corbyn, Jeremy",
        "parliament_member_id": "185",
    }
    assert packet["snapshot"]["register_as_of_date"] == "2026-07-13"
    assert packet["snapshot"]["capture_date"] == "2026-07-20"
    assert packet["snapshot"]["displayed_total_results"] == 29
    assert packet["snapshot"]["displayed_pages"] == 2
    assert packet["snapshot"]["category_counts"] == {"3": 13, "4": 12, "8": 4}
    assert "twelve months" in packet["snapshot"]["retention_statement"]

    packet_sources = by_id(packet["sources"], "source_id")
    packet_entries = by_id(packet["entries"], "entry_id")
    packet_facts = by_id(packet["facts"], "fact_id")
    packet_gaps = by_id(packet["coverage_gaps"], "gap_id")

    report_sources = by_id(report["sources"], "source_id")
    report_facts = by_id(report["facts"], "fact_id")
    report_gaps = by_id(report["coverage_gaps"], "gap_id")

    assert set(packet_sources) == OFFICIAL_SOURCE_IDS
    for source_id, source in packet_sources.items():
        assert source == report_sources[source_id]
        assert source["publisher"] == "UK Parliament"
        assert source["authority_level"] == "primary"
        assert source["source_type"] == "parliamentary_record"
        parsed = urlparse(source["url"])
        assert parsed.scheme == "https"
        assert parsed.netloc == "members.parliament.uk"

    assert len(packet_entries) == 29
    assert Counter(
        entry["category_number"] for entry in packet_entries.values()
    ) == EXPECTED_CATEGORY_COUNTS
    assert {
        entry["source_id"] for entry in packet_entries.values()
    } == ENTRY_SOURCE_IDS

    donor_names = {
        donor["name"]
        for entry in packet_entries.values()
        for donor in entry.get("donors", [])
    }
    assert "Peace and Justice Project" in donor_names
    assert "The Peace and Justice Project" in donor_names
    assert "Pece and Justice Project" in donor_names
    assert (
        packet_entries["interest-visit-2025-10-12-kuala-lumper-world-network"][
            "destination"
        ]
        == "Malaysia (Kuala Lumper)"
    )
    assert (
        packet_entries["interest-gift-2026-02-11-middlesborough-train"][
            "donors"
        ][0]["description"]
        == "Return train ticket London to Middlesborough, to attend a Your Party event"
    )
    ended_entry = packet_entries["interest-misc-your-party-uk-director"]
    assert ended_entry["date_interest_ended"] == "2026-04-21"

    assert len(packet_facts) == len(packet_entries) == 29
    for entry_id, entry in packet_entries.items():
        fact_id = f"fact-{entry_id}"
        assert fact_id in packet_facts
        fact = packet_facts[fact_id]
        assert fact == report_facts[fact_id]
        assert fact["section_id"] == "financial_interests"
        assert fact["fact_type"] == "interest"
        assert fact["confidence"] == "high"
        assert fact["evidence_status"] == "verified"
        assert fact["source_ids"] == [entry["source_id"]]
        assert set(fact["source_ids"]) <= ENTRY_SOURCE_IDS
        assert "does not by itself prove" in fact["notes"]

    financial = section(report, "financial_interests")
    assert financial["status"] == "partial"
    assert financial["fact_ids"] == list(packet_facts)
    assert financial["claim_ids"] == []
    assert financial["interpretation_ids"] == []
    assert financial["relationship_ids"] == []
    assert financial["gap_ids"] == ["gap-financial-interests-history-scope"]

    assert set(packet_gaps) == {"gap-financial-interests-history-scope"}
    assert (
        packet_gaps["gap-financial-interests-history-scope"]
        == report_gaps["gap-financial-interests-history-scope"]
    )
    assert packet_gaps["gap-financial-interests-history-scope"]["status"] == "open"
    assert (
        packet_gaps["gap-financial-interests-history-scope"]["blocks_publication"]
        is True
    )

    assert "gap-financial-interests" not in report_gaps
    assert not any(
        item["section_id"] == "financial_interests" for item in report["claims"]
    )
    assert not any(
        item["section_id"] == "financial_interests"
        for item in report["interpretations"]
    )
    assert not any(
        item["section_id"] == "financial_interests"
        for item in report["relationships"]
    )

    assert report["publication"]["status"] == "not_ready"
    assert report["publication"]["human_review_required"] is True
    assert report["publication"]["public_output_authorised"] is False


def test_deterministic_generation() -> None:
    report = load_json(FIXTURE_PATH)
    validate_report(report)

    with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
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

        profile = first_outputs["corbyn-jeremy-full-profile.md"].decode("utf-8")
        source_register = first_outputs[
            "corbyn-jeremy-source-register.md"
        ].decode("utf-8")
        coverage = first_outputs["corbyn-jeremy-coverage-report.md"].decode("utf-8")

        assert "Financial interests" in profile
        assert "Peace and Justice Project" in profile
        assert "gap-financial-interests-history-scope" in coverage
        for source_id in OFFICIAL_SOURCE_IDS:
            assert source_id in source_register


def main() -> int:
    test_packet_and_fixture()
    test_deterministic_generation()
    print("PASS — Jeremy Corbyn current financial interests baseline v1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
