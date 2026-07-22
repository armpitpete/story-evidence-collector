#!/usr/bin/env python3
"""Integrate and verify the fixed Corbyn commitments/public-positions baseline."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from generate_complete_mp_report import load_json, validate_report, write_outputs  # noqa: E402

AUTHORITY_MERGE = "4964c6b00f91c08ef9e06b5150455eaea18e8e47"
PACKET_PATH = (
    ROOT
    / "research"
    / "complete-mp-reports"
    / "jeremy-corbyn"
    / "current-parliament-commitments-and-public-positions-v1.json"
)
SOURCE_NOTE_PATH = (
    ROOT
    / "docs"
    / "jeremy-corbyn-current-parliament-commitments-and-public-positions-source-note-v1.md"
)
FIXTURE_PATH = (
    ROOT
    / "fixtures"
    / "complete-mp-reports"
    / "jeremy-corbyn-fixture-v1.json"
)
SECTION_ID = "public_positions_over_time"
GAP_ID = "gap-positions"
HANSARD_SOURCE_KEY = "hansard-current-parliament-spoken-capture"
HANSARD_SOURCE_ID = (
    "source-uk-parliament-hansard-api-corbyn-spoken-contributions-2026-07-21"
)
EXPECTED_PACKET_HASH = "fc5651b9f5647bcbfee822121f3188b0438fc826ad604351d044a8144e3df3db"
EXPECTED_CAPTURE_TIMESTAMP = "2026-07-21T13:29:25Z"
EXPECTED_COUNTS = {
    "explicit_personal_commitment": 8,
    "conditional_personal_commitment": 0,
    "collective_commitment": 8,
    "public_position": 32,
}
EXPECTED_ACCEPTED = 48
EXPECTED_UNRESOLVED = 19
EXPECTED_EXCLUDED = 42
EXPECTED_SOURCES = 8
EXPECTED_EARLIEST = "2024-07-18"
EXPECTED_LATEST = "2026-07-16"
EXPECTED_OUTPUTS = {
    "corbyn-jeremy-full-profile.json",
    "corbyn-jeremy-full-profile.md",
    "corbyn-jeremy-source-register.md",
    "corbyn-jeremy-coverage-report.md",
    "corbyn-jeremy-human-review.md",
}
FIRST_PARTY_SOURCE_IDS = {
    "jc-assisted-dying-2024-11-29":
        "source-jeremy-corbyn-assisted-dying-statement-2024-11-29",
    "jc-christmas-newsletter-2024":
        "source-jeremy-corbyn-christmas-newsletter-2024",
    "jc-ofwat-2026-02-03":
        "source-jeremy-corbyn-ofwat-deal-statement-2026-02-03",
    "pj-gaza-ceasefire-2025-01-16":
        "source-peace-justice-project-gaza-ceasefire-2025-01-16",
    "pj-gaza-inquiry-2025-06-02":
        "source-peace-justice-project-gaza-inquiry-2025-06-02",
    "pj-palestine-action-2025-06-23":
        "source-peace-justice-project-palestine-action-2025-06-23",
    "pj-gaza-tribunal-2025-07-17":
        "source-peace-justice-project-gaza-tribunal-2025-07-17",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def load_and_verify_packet() -> dict[str, Any]:
    packet = load_json(PACKET_PATH)
    recorded_hash = packet.get("capture_sha256")
    unhashed = copy.deepcopy(packet)
    unhashed.pop("capture_sha256", None)
    actual_hash = hashlib.sha256(canonical_bytes(unhashed)).hexdigest()
    assert recorded_hash == EXPECTED_PACKET_HASH
    assert actual_hash == EXPECTED_PACKET_HASH
    assert packet["authority_merge"] == AUTHORITY_MERGE
    assert packet["capture_timestamp_utc"] == EXPECTED_CAPTURE_TIMESTAMP
    assert packet["subject"]["uk_parliament_member_id"] == 185
    assert packet["date_boundary"]["authorised_from"] == "2024-07-04"
    assert packet["date_boundary"]["earliest_accepted_statement_date"] == EXPECTED_EARLIEST
    assert packet["date_boundary"]["latest_accepted_statement_date"] == EXPECTED_LATEST
    assert packet["source_inventory_count"] == EXPECTED_SOURCES
    assert len(packet["source_inventory"]) == EXPECTED_SOURCES

    fixed = packet["fixed_results"]
    assert fixed["accepted_explicit_personal_commitment_count"] == 8
    assert fixed["accepted_conditional_personal_commitment_count"] == 0
    assert fixed["accepted_collective_commitment_count"] == 8
    assert fixed["accepted_public_position_count"] == 32
    assert fixed["accepted_total_count"] == EXPECTED_ACCEPTED
    assert fixed["unresolved_statement_form_count"] == EXPECTED_UNRESOLVED
    assert fixed["excluded_candidate_count"] == EXPECTED_EXCLUDED
    assert fixed["duplicate_record_id_count"] == 0

    records = packet["accepted_records"]
    assert len(records) == EXPECTED_ACCEPTED
    record_ids = [item["record_id"] for item in records]
    assert len(record_ids) == len(set(record_ids))
    assert Counter(item["record_class"] for item in records) == Counter(EXPECTED_COUNTS)
    assert min(item["statement_date"] for item in records) == EXPECTED_EARLIEST
    assert max(item["statement_date"] for item in records) == EXPECTED_LATEST
    assert len(packet["unresolved_candidates"]) == EXPECTED_UNRESOLVED
    assert len(packet["excluded_candidates"]) == EXPECTED_EXCLUDED

    source_by_key = {item["source_key"]: item for item in packet["source_inventory"]}
    assert len(source_by_key) == EXPECTED_SOURCES
    assert HANSARD_SOURCE_KEY in source_by_key
    assert set(FIRST_PARTY_SOURCE_IDS).issubset(source_by_key)

    for source_key, source in source_by_key.items():
        if source_key == HANSARD_SOURCE_KEY:
            assert source["source_occurrence_count"] == 306
            assert source["document_sha256"] == (
                "b2776c11a5a17d9605f56434ec5b13d77e75567a9bf01f851bf48e2f440e6a88"
            )
            continue
        text = source["captured_text"]
        assert hashlib.sha256(text.encode("utf-8")).hexdigest() == (
            source["captured_text_sha256"]
        )

    for record in records:
        assert record["source_key"] in source_by_key
        assert record["statement_date"] >= "2024-07-04"
        assert record["statement_date"] <= EXPECTED_CAPTURE_TIMESTAMP[:10]
        assert record["quotation"].strip()
        assert record["quotation"] in record["surrounding_context"]
        if record["source_key"] != HANSARD_SOURCE_KEY:
            assert record["quotation"] in source_by_key[record["source_key"]]["captured_text"]
        if record["record_class"] == "collective_commitment":
            assert record["actor"] == "collective_we"
        if record["record_class"] == "conditional_personal_commitment":
            assert record["explicit_condition"]

    boundary = packet["interpretation_boundary"]
    assert boundary == {
        "conduct_comparison_performed": False,
        "delivery_or_broken_promise_verdicts_created": False,
        "topic_or_ideology_classification_created": False,
        "contradiction_analysis_created": False,
        "fixture_modified": False,
        "publication_authorised": False,
    }
    return packet


def load_authority_fixture() -> dict[str, Any]:
    relative = FIXTURE_PATH.relative_to(ROOT).as_posix()
    raw = subprocess.check_output(
        ["git", "show", f"{AUTHORITY_MERGE}:{relative}"],
        cwd=ROOT,
    )
    value = json.loads(raw.decode("utf-8"))
    assert isinstance(value, dict)
    return value


def section(report: dict[str, Any], section_id: str) -> dict[str, Any]:
    return next(item for item in report["sections"] if item["section_id"] == section_id)


def gap(report: dict[str, Any], gap_id: str) -> dict[str, Any]:
    return next(item for item in report["coverage_gaps"] if item["gap_id"] == gap_id)


def source_id_for(source_key: str) -> str:
    if source_key == HANSARD_SOURCE_KEY:
        return HANSARD_SOURCE_ID
    return FIRST_PARTY_SOURCE_IDS[source_key]


def expected_sources(packet: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for source in packet["source_inventory"]:
        source_key = source["source_key"]
        if source_key == HANSARD_SOURCE_KEY:
            continue
        publication_date = source["publication_date"]
        results.append(
            {
                "source_id": source_id_for(source_key),
                "title": source["title"],
                "publisher": source["publisher"],
                "source_type": "other",
                "authority_level": "primary",
                "url": source["url"],
                "repository_path": (
                    "research/complete-mp-reports/jeremy-corbyn/"
                    "current-parliament-commitments-and-public-positions-v1.json"
                ),
                "server_path": "",
                "publication_date": publication_date,
                "capture_date": EXPECTED_CAPTURE_TIMESTAMP[:10],
                "coverage_from": publication_date,
                "coverage_to": publication_date,
                "checksum": "sha256:" + source["captured_text_sha256"],
                "limitations": (
                    "First-party source establishing the attributable statement text "
                    "preserved in the fixed packet. It does not establish delivery, "
                    "accuracy, significance, motive, sincerity or later consistency."
                ),
            }
        )
    assert len(results) == 7
    return results


def fact_id(record: dict[str, Any]) -> str:
    suffix = record["record_id"]
    assert suffix.startswith("statement-")
    return "fact-position-" + suffix.removeprefix("statement-")


def expected_facts(packet: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    ordered = sorted(
        packet["accepted_records"],
        key=lambda item: (
            item["statement_date"],
            item["source_key"],
            item["record_id"],
        ),
    )
    for record in ordered:
        record_class = record["record_class"]
        if record["actor"] == "collective_we":
            lead = "The fixed source records this collective statement occurrence"
        else:
            lead = "The fixed source records Jeremy Corbyn stating"
        statement = (
            f"On {record['statement_date']}, {lead}, classified only by its "
            f"literal form as {record_class}: “{record['quotation']}”"
        )
        note_value = {
            "statement_record_id": record["record_id"],
            "statement_form": record_class,
            "exact_quotation": record["quotation"],
            "surrounding_context": record["surrounding_context"],
            "actor": record["actor"],
            "collective_issuer": record.get("collective_issuer"),
            "explicit_condition": record.get("explicit_condition"),
            "explicit_deadline": record.get("explicit_deadline"),
            "delivery_assessment": None,
            "contradiction_assessment": None,
        }
        results.append(
            {
                "fact_id": fact_id(record),
                "section_id": SECTION_ID,
                "statement": statement,
                "fact_type": "position",
                "date": record["statement_date"],
                "date_from": None,
                "date_to": None,
                "source_ids": [source_id_for(record["source_key"])],
                "confidence": "high",
                "evidence_status": "verified",
                "notes": json.dumps(
                    note_value,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            }
        )
    assert len(results) == EXPECTED_ACCEPTED
    assert len({item["fact_id"] for item in results}) == EXPECTED_ACCEPTED
    return results


def expected_gap(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "gap_id": GAP_ID,
        "section_id": SECTION_ID,
        "summary": (
            "The bounded current-Parliament baseline contains 48 accepted statement "
            "occurrences from eight fixed source documents or pages. It is not an "
            "exhaustive position history, and 19 candidate statement forms remain "
            "unresolved without interpretation."
        ),
        "severity": "blocking",
        "reason": "human_review_pending",
        "date_from": "2024-07-04",
        "date_to": EXPECTED_CAPTURE_TIMESTAMP[:10],
        "status": "open",
        "blocks_publication": True,
        "next_action": (
            "Review unresolved statement forms and separately authorise any historic, "
            "future-refresh or commitment-versus-conduct comparison lane."
        ),
        "notes": (
            "Excluded source classes, pre-4-July-2024 material, later updates and "
            "conduct comparison remain outside this baseline. Absence from the fixed "
            "inventory is not evidence that no other commitment or position existed."
        ),
    }


def build_expected_fixture(
    packet: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, Any]:
    report = copy.deepcopy(baseline)
    existing_source_ids = {item["source_id"] for item in report["sources"]}
    assert HANSARD_SOURCE_ID in existing_source_ids
    new_sources = expected_sources(packet)
    assert not (existing_source_ids & {item["source_id"] for item in new_sources})
    report["sources"].extend(new_sources)

    new_facts = expected_facts(packet)
    existing_fact_ids = {item["fact_id"] for item in report["facts"]}
    assert not (existing_fact_ids & {item["fact_id"] for item in new_facts})
    report["facts"].extend(new_facts)

    target = section(report, SECTION_ID)
    assert target["fact_ids"] == []
    assert target["claim_ids"] == []
    assert target["interpretation_ids"] == []
    assert target["relationship_ids"] == []
    assert target["gap_ids"] == [GAP_ID]
    target["status"] = "partial"
    target["summary"] = (
        "A fixed current-Parliament primary-source baseline records 48 dated "
        "statement occurrences from 18 July 2024 through 16 July 2026: "
        "eight explicit personal commitments, no conditional personal commitments, "
        "eight collective commitments and 32 public positions. Nineteen candidate "
        "statement forms remain unresolved; no conduct or contradiction assessment "
        "has been made."
    )
    target["fact_ids"] = [item["fact_id"] for item in new_facts]

    gaps = report["coverage_gaps"]
    target_index = next(
        index for index, item in enumerate(gaps) if item["gap_id"] == GAP_ID
    )
    gaps[target_index] = expected_gap(packet)
    return report


def verify_protected_baseline(
    current: dict[str, Any],
    baseline: dict[str, Any],
    packet: dict[str, Any],
) -> None:
    assert current["subject"] == baseline["subject"]
    assert current["scope"] == baseline["scope"]
    assert current["publication"] == baseline["publication"]
    assert current["claims"] == baseline["claims"]
    assert current["interpretations"] == baseline["interpretations"]
    assert current["relationships"] == baseline["relationships"]
    assert current["review_decisions"] == baseline["review_decisions"]

    baseline_sections = {
        item["section_id"]: item for item in baseline["sections"]
    }
    current_sections = {
        item["section_id"]: item for item in current["sections"]
    }
    for section_id, value in baseline_sections.items():
        if section_id != SECTION_ID:
            assert current_sections[section_id] == value

    baseline_gaps = {
        item["gap_id"]: item for item in baseline["coverage_gaps"]
    }
    current_gaps = {
        item["gap_id"]: item for item in current["coverage_gaps"]
    }
    for gap_id, value in baseline_gaps.items():
        if gap_id != GAP_ID:
            assert current_gaps[gap_id] == value

    new_sources = expected_sources(packet)
    assert current["sources"] == baseline["sources"] + new_sources
    new_facts = expected_facts(packet)
    assert current["facts"] == baseline["facts"] + new_facts

    target = current_sections[SECTION_ID]
    assert target["status"] == "partial"
    assert target["fact_ids"] == [item["fact_id"] for item in new_facts]
    assert target["claim_ids"] == []
    assert target["interpretation_ids"] == []
    assert target["relationship_ids"] == []
    assert target["gap_ids"] == [GAP_ID]
    assert current_gaps[GAP_ID] == expected_gap(packet)

    changes = current_sections["changes_and_contradictions"]
    assert changes == baseline_sections["changes_and_contradictions"]
    assert changes["status"] == "human_review_required"

    question_ids = [
        item["fact_id"]
        for item in current["facts"]
        if item["fact_type"] == "question"
    ]
    baseline_question_ids = [
        item["fact_id"]
        for item in baseline["facts"]
        if item["fact_type"] == "question"
    ]
    assert question_ids == baseline_question_ids
    assert len(question_ids) == 90

    assert current["publication"]["status"] == "not_ready"
    assert current["publication"]["human_review_required"] is True
    assert current["publication"]["public_output_authorised"] is False


def verify_source_note() -> None:
    text = SOURCE_NOTE_PATH.read_text(encoding="utf-8")
    for required in (
        "**8** source documents or pages",
        "**48** accepted neutral statement occurrences",
        "**8** explicit personal commitments",
        "**0** conditional personal commitments",
        "**8** collective commitments",
        "**32** public positions",
        "**19** unresolved statement forms",
        EXPECTED_PACKET_HASH,
        "`public_positions_over_time` remains `partial`",
    ):
        assert required in text


def verify_outputs(report: dict[str, Any]) -> None:
    with tempfile.TemporaryDirectory() as temporary:
        output_dir = Path(temporary)
        write_outputs(report, output_dir)
        assert {path.name for path in output_dir.iterdir()} == EXPECTED_OUTPUTS
        for path in output_dir.iterdir():
            assert path.stat().st_size > 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--integrate", action="store_true")
    args = parser.parse_args()

    packet = load_and_verify_packet()
    baseline = load_authority_fixture()
    expected = build_expected_fixture(packet, baseline)
    validate_report(expected)

    if args.integrate:
        FIXTURE_PATH.write_text(
            json.dumps(expected, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    current = load_json(FIXTURE_PATH)
    assert current == expected
    validate_report(current)
    verify_protected_baseline(current, baseline, packet)
    verify_source_note()
    verify_outputs(current)

    print(
        "PASS — fixed commitments/public-positions baseline: "
        "8 sources, 48 accepted, 19 unresolved, 42 excluded"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
