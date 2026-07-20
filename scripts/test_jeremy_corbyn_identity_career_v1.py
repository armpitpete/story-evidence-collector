#!/usr/bin/env python3
"""Regression proof for Jeremy Corbyn identity and career baseline v1."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from generate_complete_mp_report import load_json, validate_report, write_outputs

ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = (
    ROOT
    / "research"
    / "complete-mp-reports"
    / "jeremy-corbyn"
    / "identity-and-parliamentary-career-v1.json"
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
    "source-uk-parliament-member-career",
    "source-uk-parliament-2024-election-result",
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


def test_packet_and_fixture() -> None:
    packet = load_packet()
    report = load_json(FIXTURE_PATH)
    validate_report(report)

    assert packet["section_id"] == "identity_and_parliamentary_career"
    assert packet["subject"] == {
        "official_name": "Jeremy Corbyn",
        "repository_display_name": "Corbyn, Jeremy",
        "parliament_member_id": "185",
    }

    packet_sources = by_id(packet["sources"], "source_id")
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
        assert source["source_type"] in {"parliamentary_record", "electoral_record"}
        parsed = urlparse(source["url"])
        assert parsed.scheme == "https"
        assert parsed.netloc == "members.parliament.uk"
        assert parsed.path.startswith("/member/185/")

    identity = report["subject"]
    assert identity["display_name"] == "Corbyn, Jeremy"
    assert identity["parliament_member_id"] == "185"
    assert identity["current_constituency"] == "Islington North"
    assert identity["current_party"] == "Your Party"
    assert identity["identity_status"] == "verified"
    assert set(identity["identity_source_ids"]) == OFFICIAL_SOURCE_IDS

    identity_section = section(report, "identity_and_parliamentary_career")
    assert identity_section["status"] == "partial"
    assert identity_section["fact_ids"] == list(packet_facts)
    assert identity_section["gap_ids"] == [
        "gap-identity-refresh",
        "gap-career-history-scope",
    ]

    for fact_id, fact in packet_facts.items():
        assert fact == report_facts[fact_id]
        assert fact["section_id"] == "identity_and_parliamentary_career"
        assert fact["confidence"] == "high"
        assert fact["evidence_status"] == "verified"
        assert set(fact["source_ids"]) <= OFFICIAL_SOURCE_IDS

    assert (
        report_facts["fact-party-your-party-2026-present"]["date_from"]
        == "2026-06-10"
    )
    assert (
        report_facts["fact-2024-election-independent"]["date"]
        == "2024-07-04"
    )
    assert "Independent" in report_facts["fact-2024-election-independent"]["statement"]
    assert (
        report_facts["fact-party-your-party-2026-present"]["statement"]
        != report_facts["fact-2024-election-independent"]["statement"]
    )

    for gap_id, gap in packet_gaps.items():
        assert gap == report_gaps[gap_id]

    assert report_gaps["gap-identity-refresh"]["status"] == "resolved"
    assert report_gaps["gap-identity-refresh"]["blocks_publication"] is False
    assert report_gaps["gap-career-history-scope"]["status"] == "open"
    assert report_gaps["gap-career-history-scope"]["blocks_publication"] is True

    assert report["scope"]["career_start_date"] == "1983-06-09"
    assert report["scope"]["as_of_date"] == "2026-07-20"
    assert report["publication"]["status"] == "not_ready"
    assert report["publication"]["human_review_required"] is True
    assert report["publication"]["public_output_authorised"] is False
    assert report["interpretations"] == []
    assert report["relationships"] == []

    official_fact_ids = set(packet_facts)
    for fact in report["facts"]:
        if fact["fact_id"] not in official_fact_ids:
            assert fact["section_id"] != "identity_and_parliamentary_career"


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
        assert "Islington North" in profile
        assert "Your Party" in profile
        assert "source-uk-parliament-member-career" in source_register
        assert "source-uk-parliament-2024-election-result" in source_register


def main() -> int:
    test_packet_and_fixture()
    test_deterministic_generation()
    print("PASS — Jeremy Corbyn official identity and career baseline v1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
