#!/usr/bin/env python3
"""Integrate and validate the fixed Jeremy Corbyn current-Parliament EDM records."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = (
    ROOT
    / "research"
    / "complete-mp-reports"
    / "jeremy-corbyn"
    / "current-parliament-early-day-motions-source-inventory-v1.json"
)
FIXTURE_PATH = (
    ROOT
    / "fixtures"
    / "complete-mp-reports"
    / "jeremy-corbyn-fixture-v1.json"
)

EXPECTED_INVENTORY_ID = (
    "jeremy-corbyn-current-parliament-early-day-motions-source-inventory-v1"
)
EXPECTED_CAPTURE_SHA256 = (
    "4558d82deddbee2168449d64aa4998672ae08faf212ac1338ce17fb8bab0304a"
)
EXPECTED_MOTION_IDS = (62446, 63037, 64576, 65102, 65889, 66149)
SOURCE_ID = (
    "source-uk-parliament-corbyn-current-parliament-early-day-motions-2026-07-22"
)
SECTION_ID = "speeches_and_questions"
EXPECTED_SUMMARY = (
    "Official UK Parliament records identify 90 Commons written questions tabled "
    "by Jeremy Corbyn in the current Parliament, 306 individual Commons Chamber "
    "or Westminster Hall spoken contributions from 17 July 2024 through the fixed "
    "21 July 2026 capture, and six Early Day Motions officially tabled by him from "
    "2 September 2024 through 23 June 2026. Earlier and future records, later "
    "corrections and adjacent parliamentary record types remain outside the "
    "completed bounded baselines."
)
FORBIDDEN_FACT_LANGUAGE = (
    "commitment",
    "public position",
    "delivery",
    "fulfilment",
    "broken promise",
    "contradiction",
    "ideology",
    "motive",
    "importance",
    "influence",
    "effectiveness",
    "success",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def validate_inventory(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    if inventory.get("inventory_id") != EXPECTED_INVENTORY_ID:
        fail("fixed EDM inventory identity changed")
    supplied = inventory.get("capture_sha256")
    if supplied != EXPECTED_CAPTURE_SHA256:
        fail("fixed EDM inventory capture checksum changed")
    unhashed = copy.deepcopy(inventory)
    unhashed.pop("capture_sha256", None)
    if sha256_value(unhashed) != supplied:
        fail("fixed EDM inventory checksum does not validate")
    motions = inventory.get("motions")
    if not isinstance(motions, list):
        fail("fixed EDM inventory motions are missing")
    by_id = {row.get("official_motion_id"): row for row in motions}
    if tuple(sorted(by_id)) != EXPECTED_MOTION_IDS or len(motions) != 6:
        fail("fixed EDM motion set changed")
    return [by_id[motion_id] for motion_id in EXPECTED_MOTION_IDS]


def source_record() -> dict[str, Any]:
    return {
        "source_id": SOURCE_ID,
        "title": (
            "UK Parliament current-Parliament Early Day Motions tabled by "
            "Jeremy Corbyn — fixed inventory"
        ),
        "publisher": "UK Parliament",
        "source_type": "parliamentary_record",
        "authority_level": "primary",
        "url": (
            "https://oralquestionsandmotions-api.parliament.uk/"
            "EarlyDayMotions/list?parameters.memberId=185&"
            "parameters.includeSponsoredByMember=false&"
            "parameters.tabledStartDate=2024-07-04&"
            "parameters.tabledEndDate=2026-07-22&"
            "parameters.statuses=Published&parameters.statuses=Withdrawn&"
            "parameters.skip=0&parameters.take=100"
        ),
        "repository_path": (
            "research/complete-mp-reports/jeremy-corbyn/"
            "current-parliament-early-day-motions-source-inventory-v1.json"
        ),
        "server_path": "",
        "publication_date": None,
        "capture_date": "2026-07-22",
        "coverage_from": "2024-09-02",
        "coverage_to": "2026-06-23",
        "checksum": f"sha256:{EXPECTED_CAPTURE_SHA256}",
        "limitations": (
            "Fixed six-record current-Parliament tabled-by-member inventory. "
            "Signature totals are capture-time snapshots. Motions merely signed "
            "or secondarily sponsored by Jeremy Corbyn, pre-4-July-2024 records, "
            "later source changes and publication assessment are outside this source."
        ),
    }


def fact_id(motion_id: int) -> str:
    return f"fact-early-day-motion-{motion_id}"


def fact_statement(motion: dict[str, Any]) -> str:
    return (
        f"On {motion['tabled_date']}, UK Parliament recorded Jeremy Corbyn as "
        f"the primary sponsor of Early Day Motion {motion['edm_number']}, "
        f"“{motion['title']}” (official motion ID {motion['official_motion_id']})."
    )


def fact_notes(motion: dict[str, Any]) -> str:
    snapshot = motion["signature_snapshot"]
    unresolved = ", ".join(motion["unresolved_fields"])
    return (
        f"Fixed source record {motion['record_id']}; session {motion['session']}; "
        f"official page {motion['official_url']}; API detail "
        f"{motion['official_api_url']}; capture-time signatures "
        f"{snapshot['total']} total, {snapshot['supporters']} not withdrawn and "
        f"{snapshot['withdrawn']} withdrawn; unresolved fields: {unresolved}. "
        "Full official motion text and detail checksum remain in the fixed packet."
    )


def fact_record(motion: dict[str, Any]) -> dict[str, Any]:
    return {
        "fact_id": fact_id(motion["official_motion_id"]),
        "section_id": SECTION_ID,
        "statement": fact_statement(motion),
        "fact_type": "other",
        "date": motion["tabled_date"],
        "date_from": None,
        "date_to": None,
        "source_ids": [SOURCE_ID],
        "confidence": "high",
        "evidence_status": "verified",
        "notes": fact_notes(motion),
    }


def find_section(fixture: dict[str, Any]) -> dict[str, Any]:
    matches = [
        item
        for item in fixture.get("sections", [])
        if item.get("section_id") == SECTION_ID
    ]
    if len(matches) != 1:
        fail("speeches_and_questions section is missing or duplicated")
    return matches[0]


def apply_integration(
    fixture: dict[str, Any],
    motions: list[dict[str, Any]],
) -> None:
    expected_source = source_record()
    sources = fixture.setdefault("sources", [])
    source_matches = [
        item for item in sources if item.get("source_id") == SOURCE_ID
    ]
    if not source_matches:
        sources.append(expected_source)
    elif len(source_matches) == 1:
        source_matches[0].clear()
        source_matches[0].update(expected_source)
    else:
        fail("canonical EDM source is duplicated")

    expected_facts = {
        fact["fact_id"]: fact for fact in (fact_record(row) for row in motions)
    }
    facts = fixture.setdefault("facts", [])
    retained = [
        item
        for item in facts
        if not str(item.get("fact_id", "")).startswith("fact-early-day-motion-")
    ]
    fixture["facts"] = retained + list(expected_facts.values())

    section = find_section(fixture)
    retained_ids = [
        value
        for value in section.get("fact_ids", [])
        if not str(value).startswith("fact-early-day-motion-")
    ]
    section["fact_ids"] = retained_ids + list(expected_facts)
    section["summary"] = EXPECTED_SUMMARY
    section["status"] = "partial"


def validate_integration(
    fixture: dict[str, Any],
    motions: list[dict[str, Any]],
) -> None:
    sources = [
        item
        for item in fixture.get("sources", [])
        if item.get("source_id") == SOURCE_ID
    ]
    if sources != [source_record()]:
        fail("canonical fixed-inventory source is missing, duplicated or changed")

    expected = {
        fact["fact_id"]: fact for fact in (fact_record(row) for row in motions)
    }
    actual = {
        item["fact_id"]: item
        for item in fixture.get("facts", [])
        if str(item.get("fact_id", "")).startswith("fact-early-day-motion-")
    }
    if set(actual) != set(expected) or len(actual) != 6:
        fail("canonical EDM fact set is missing, duplicated or expanded")
    for key, value in expected.items():
        if actual[key] != value:
            fail(f"canonical EDM fact changed: {key}")
        combined = f"{actual[key]['statement']} {actual[key]['notes']}".lower()
        for forbidden in FORBIDDEN_FACT_LANGUAGE:
            if forbidden in combined:
                fail(f"interpretive language entered {key}: {forbidden}")

    section = find_section(fixture)
    if section.get("status") != "partial":
        fail("speeches_and_questions must remain partial")
    if section.get("summary") != EXPECTED_SUMMARY:
        fail("speeches_and_questions summary changed")
    edm_ids = [
        value
        for value in section.get("fact_ids", [])
        if str(value).startswith("fact-early-day-motion-")
    ]
    if edm_ids != list(expected):
        fail("section EDM fact references are incomplete, duplicated or reordered")

    fact_ids = set(expected)
    for collection_name, id_key, source_key, fact_key in (
        ("claims", "claim_id", "source_ids", "fact_ids"),
        ("interpretations", "interpretation_id", None, "fact_ids"),
        ("relationships", "relationship_id", "source_ids", None),
    ):
        for item in fixture.get(collection_name, []):
            if str(item.get(id_key, "")).startswith(
                (
                    "claim-early-day-motion-",
                    "interpretation-early-day-motion-",
                    "relationship-early-day-motion-",
                )
            ):
                fail(f"EDM-derived {collection_name} record is forbidden")
            if source_key and SOURCE_ID in item.get(source_key, []):
                fail(f"EDM source entered {collection_name}")
            if fact_key and fact_ids.intersection(item.get(fact_key, [])):
                fail(f"EDM facts entered {collection_name}")

    publication = fixture.get("publication", {})
    if (
        publication.get("status") != "not_ready"
        or publication.get("human_review_required") is not True
        or publication.get("public_output_authorised") is not False
    ):
        fail("publication boundary changed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="apply the deterministic three-file-authorised fixture integration",
    )
    args = parser.parse_args()

    inventory = load_json(INVENTORY_PATH)
    motions = validate_inventory(inventory)
    fixture = load_json(FIXTURE_PATH)

    if args.apply:
        apply_integration(fixture, motions)
        FIXTURE_PATH.write_text(
            json.dumps(fixture, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        fixture = load_json(FIXTURE_PATH)

    validate_integration(fixture, motions)
    print(
        "PASS: six fixed current-Parliament EDM records are neutrally integrated "
        "into the canonical fixture"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
