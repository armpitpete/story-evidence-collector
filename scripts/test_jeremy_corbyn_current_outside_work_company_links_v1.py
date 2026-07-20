#!/usr/bin/env python3
"""Regression proof for Jeremy Corbyn current outside-work company links v1."""

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
    / "current-outside-work-company-links-v1.json"
)
FIXTURE_PATH = (
    ROOT
    / "fixtures"
    / "complete-mp-reports"
    / "jeremy-corbyn-fixture-v1.json"
)

PARLIAMENT_SOURCE_ID = "source-uk-parliament-registered-interests-current"
COMPANY_NUMBERS = {
    "company-link-your-party-uk-ltd": "16619803",
    "company-link-jeremy-corbyn-campaign-limited": "15977146",
    "company-link-community-unity-ltd": "15392819",
    "company-link-peace-and-justice-project-ltd": "12945855",
}
FACT_IDS = [
    "fact-company-link-your-party-uk-ltd",
    "fact-company-link-jeremy-corbyn-campaign-limited",
    "fact-company-link-community-unity-ltd",
    "fact-company-link-peace-and-justice-project-ltd",
]
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


def test_packet_and_fixture() -> None:
    packet = load_packet()
    report = load_json(FIXTURE_PATH)
    validate_report(report)

    assert packet["section_id"] == "outside_work_and_company_links"
    assert packet["subject"]["parliament_member_id"] == "185"
    assert packet["existing_source_ids"] == [PARLIAMENT_SOURCE_ID]

    report_sources = by_id(report["sources"], "source_id")
    assert PARLIAMENT_SOURCE_ID in report_sources

    packet_sources = by_id(packet["sources"], "source_id")
    assert len(packet_sources) == 8
    for source_id, source in packet_sources.items():
        assert source == report_sources[source_id]
        assert source["publisher"] == "Companies House"
        assert source["authority_level"] == "primary"
        assert source["source_type"] == "company_registry"
        parsed = urlparse(source["url"])
        assert parsed.scheme == "https"
        assert parsed.netloc == "find-and-update.company-information.service.gov.uk"
        assert source["capture_date"] == "2026-07-20"

    companies = by_id(packet["companies"], "link_id")
    assert {
        link_id: item["registry"]["company_number"]
        for link_id, item in companies.items()
    } == COMPANY_NUMBERS

    assert companies["company-link-your-party-uk-ltd"]["registry"][
        "company_status"
    ] == "dissolved"
    assert companies["company-link-your-party-uk-ltd"]["registry"][
        "dissolved_on"
    ] == "2026-04-21"

    campaign = companies["company-link-jeremy-corbyn-campaign-limited"]
    assert campaign["registry"]["company_name"] == "JEREMY CORBYN CAMPAIGN LIMITED"
    assert campaign["registry"]["company_status"] == "active"
    assert campaign["registry"]["subject_officer"]["appointed_on"] == "2024-09-25"

    community = companies["company-link-community-unity-ltd"]
    assert community["declared_role_type"] == "unpaid_bank_signatory"
    assert community["registry"]["company_status"] == "dissolved"
    assert community["registry"]["dissolved_on"] == "2025-05-20"
    assert community["registry"]["subject_officer_listed"] is False
    assert community["registry"]["subject_officer"] is None
    assert community["registry"]["officer_page_count"] == 4

    peace = companies["company-link-peace-and-justice-project-ltd"]
    assert peace["registry"]["company_name"] == "PEACE AND JUSTICE PROJECT LTD"
    assert peace["registry"]["company_status"] == "active"
    assert peace["registry"]["subject_officer"]["appointed_on"] == "2020-10-13"

    packet_facts = by_id(packet["facts"], "fact_id")
    report_facts = by_id(report["facts"], "fact_id")
    assert list(packet_facts) == FACT_IDS

    outside = section(report, "outside_work_and_company_links")
    assert outside["status"] == "partial"
    assert outside["fact_ids"] == FACT_IDS
    assert outside["claim_ids"] == []
    assert outside["interpretation_ids"] == []
    assert outside["relationship_ids"] == []
    assert outside["gap_ids"] == ["gap-outside-work-company-history-scope"]

    for fact_id, fact in packet_facts.items():
        assert fact == report_facts[fact_id]
        assert fact["section_id"] == "outside_work_and_company_links"
        assert fact["fact_type"] == "company"
        assert fact["confidence"] == "high"
        assert fact["evidence_status"] == "verified"
        assert fact["source_ids"][0] == PARLIAMENT_SOURCE_ID
        assert len(fact["source_ids"]) == 3

    community_fact = packet_facts["fact-company-link-community-unity-ltd"]
    assert community_fact["date_to"] is None
    assert "bank signatory" in community_fact["statement"]
    assert "does not list Jeremy Corbyn" in community_fact["statement"]
    assert "not reclassified" in community_fact["notes"]

    packet_gaps = by_id(packet["coverage_gaps"], "gap_id")
    report_gaps = by_id(report["coverage_gaps"], "gap_id")
    assert set(packet_gaps) == {"gap-outside-work-company-history-scope"}
    assert packet_gaps["gap-outside-work-company-history-scope"] == report_gaps[
        "gap-outside-work-company-history-scope"
    ]
    assert "gap-outside-work" not in report_gaps
    assert report_gaps["gap-outside-work-company-history-scope"]["status"] == "open"
    assert report_gaps["gap-outside-work-company-history-scope"][
        "blocks_publication"
    ] is True

    assert not any(
        item["section_id"] == "outside_work_and_company_links"
        for item in report["claims"]
    )
    assert not any(
        item["section_id"] == "outside_work_and_company_links"
        for item in report["interpretations"]
    )
    assert not any(
        item["section_id"] == "outside_work_and_company_links"
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

        for number in COMPANY_NUMBERS.values():
            assert number in profile
        assert "unpaid bank signatory" in profile
        assert "gap-outside-work-company-history-scope" in coverage
        for source_id in by_id(load_packet()["sources"], "source_id"):
            assert source_id in source_register


def main() -> int:
    test_packet_and_fixture()
    test_deterministic_generation()
    print(
        "PASS - Jeremy Corbyn current outside work and company links baseline v1"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
