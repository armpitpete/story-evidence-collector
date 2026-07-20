#!/usr/bin/env python3
"""Regression proof for Jeremy Corbyn roles and committees baseline v1."""

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
    / "roles-and-committees-v1.json"
)
FIXTURE_PATH = (
    ROOT
    / "fixtures"
    / "complete-mp-reports"
    / "jeremy-corbyn-fixture-v1.json"
)

OFFICIAL_SOURCE_IDS = {
    "source-uk-parliament-member-career",
    "source-uk-parliament-social-security-committee",
    "source-uk-parliament-justice-committee",
}
ROLE_FACT_IDS = [
    "fact-role-parliamentary-leader-your-party",
    "fact-role-labour-party-leader-2015-2020",
    "fact-role-official-opposition-leader-2015-2020",
]
COMMITTEE_FACT_IDS = [
    "fact-committee-social-security-1992-1997",
    "fact-committee-justice-2011-2015",
]
LANE_FACT_IDS = ROLE_FACT_IDS + COMMITTEE_FACT_IDS
PROTECTED_FACT_IDS = {
    "fact-fixture-member-id",
    "fact-current-constituency",
    "fact-continuous-commons-service",
    "fact-representation-1983-1997",
    "fact-representation-1997-2010",
    "fact-representation-2010-2024",
    "fact-representation-2024-present",
    "fact-party-labour-1983-2020",
    "fact-party-independent-2020-2026",
    "fact-party-your-party-2026-present",
    "fact-2024-election-independent",
    "fact-vote-workflow-exists",
    "fact-historic-plan-range",
    "fact-server-live-state-unverified",
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
    return next(
        item for item in report["sections"] if item["section_id"] == section_id
    )


def test_packet_and_fixture() -> None:
    packet = load_packet()
    report = load_json(FIXTURE_PATH)
    validate_report(report)

    assert packet["section_id"] == "roles_and_committees"
    assert packet["subject"]["parliament_member_id"] == "185"

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
        assert source["source_type"] == "parliamentary_record"
        parsed = urlparse(source["url"])
        assert parsed.scheme == "https"
        assert parsed.netloc in {
            "members.parliament.uk",
            "committees.parliament.uk",
        }

    assert list(packet_facts) == LANE_FACT_IDS
    roles_section = section(report, "roles_and_committees")
    assert roles_section["status"] == "partial"
    assert roles_section["fact_ids"] == LANE_FACT_IDS
    assert roles_section["claim_ids"] == []
    assert roles_section["interpretation_ids"] == []
    assert roles_section["relationship_ids"] == []
    assert roles_section["gap_ids"] == ["gap-role-committee-history-scope"]

    for fact_id, fact in packet_facts.items():
        assert fact == report_facts[fact_id]
        assert fact["section_id"] == "roles_and_committees"
        assert fact["confidence"] == "high"
        assert fact["evidence_status"] == "verified"
        assert set(fact["source_ids"]) <= OFFICIAL_SOURCE_IDS

    assert [report_facts[fact_id]["fact_type"] for fact_id in ROLE_FACT_IDS] == [
        "role",
        "role",
        "role",
    ]
    assert [
        report_facts[fact_id]["fact_type"] for fact_id in COMMITTEE_FACT_IDS
    ] == ["committee", "committee"]

    assert (
        report_facts["fact-role-parliamentary-leader-your-party"]["date_from"]
        == "2026-06-10"
    )
    assert (
        report_facts["fact-role-labour-party-leader-2015-2020"]["date_from"]
        == "2015-09-12"
    )
    assert (
        report_facts["fact-role-labour-party-leader-2015-2020"]["date_to"]
        == "2020-04-04"
    )
    assert (
        report_facts["fact-role-official-opposition-leader-2015-2020"][
            "statement"
        ]
        != report_facts["fact-role-labour-party-leader-2015-2020"]["statement"]
    )
    assert (
        report_facts["fact-committee-social-security-1992-1997"]["date_from"]
        == "1992-04-27"
    )
    assert (
        report_facts["fact-committee-social-security-1992-1997"]["date_to"]
        == "1997-03-21"
    )
    assert (
        report_facts["fact-committee-justice-2011-2015"]["date_from"]
        == "2011-05-16"
    )
    assert (
        report_facts["fact-committee-justice-2011-2015"]["date_to"]
        == "2015-03-30"
    )

    non_lane_fact_ids = set(report_facts) - set(LANE_FACT_IDS)
    assert non_lane_fact_ids == PROTECTED_FACT_IDS
    for fact_id in PROTECTED_FACT_IDS:
        assert report_facts[fact_id]["section_id"] != "roles_and_committees"

    assert set(packet_gaps) == {"gap-role-committee-history-scope"}
    assert packet_gaps["gap-role-committee-history-scope"] == report_gaps[
        "gap-role-committee-history-scope"
    ]
    assert "gap-roles" not in report_gaps
    assert report_gaps["gap-role-committee-history-scope"]["status"] == "open"
    assert (
        report_gaps["gap-role-committee-history-scope"]["blocks_publication"]
        is True
    )

    assert report["subject"]["identity_status"] == "verified"
    assert report["subject"]["current_constituency"] == "Islington North"
    assert report["subject"]["current_party"] == "Your Party"
    assert report["publication"]["status"] == "not_ready"
    assert report["publication"]["human_review_required"] is True
    assert report["publication"]["public_output_authorised"] is False
    assert report["interpretations"] == []
    assert report["relationships"] == []


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
        assert "Parliamentary Leader, Your Party" in profile
        assert "Leader of the Labour Party" in profile
        assert "Leader of HM Official Opposition" in profile
        assert "Social Security Commons Select Committee" in profile
        assert "Justice Committee, a Commons Select Committee" in profile
        for source_id in OFFICIAL_SOURCE_IDS:
            assert source_id in source_register


def main() -> int:
    test_packet_and_fixture()
    test_deterministic_generation()
    print("PASS — Jeremy Corbyn official roles and committees baseline v1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
