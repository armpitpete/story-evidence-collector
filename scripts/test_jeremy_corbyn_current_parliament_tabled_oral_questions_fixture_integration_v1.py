#!/usr/bin/env python3
"""Validate and deterministically build the bounded oral-question fixture integration."""
from __future__ import annotations

import argparse
import base64
import copy
import gzip
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_REL = "fixtures/complete-mp-reports/jeremy-corbyn-fixture-v1.json"
INVENTORY_REL = (
    "research/complete-mp-reports/jeremy-corbyn/"
    "current-parliament-tabled-oral-questions-source-inventory-v1.json"
)
FIXTURE = ROOT / FIXTURE_REL
INVENTORY = ROOT / INVENTORY_REL
BASE_COMMIT = "40ad51d0f1e9f999b9731323dfb0600101046c5d"
BASE_FIXTURE_BLOB = "78d8f41c3fc23a3afc7ddde066dce8348a2d2d10"
INVENTORY_BLOB = "f4dd38add4b08f4c0aa90943fcdcbf4fa30653d7"
INVENTORY_ID = (
    "jeremy-corbyn-current-parliament-tabled-oral-questions-source-inventory-v1"
)
SOURCE_ID = (
    "source-uk-parliament-corbyn-current-parliament-"
    "tabled-oral-questions-2026-07-23"
)
OFFICIAL_URL = (
    "https://oralquestionsandmotions-api.parliament.uk/oralquestions/list"
    "?parameters.askingMemberIds=185&parameters.skip=0&parameters.take=100"
)
CAPTURED_AT = "2026-07-23T17:27:27Z"
RAW_SHA256 = "9d3b31f77d8e53c018039713fad830bc1e99b73bc5ca7c6a7bd0d67603cd35f9"
GZIP_SHA256 = "b7126e70594e3d4ce468e00f26dddb13ca5606de9dd1fed26ac138a5d6071a7f"
PACKET_SHA256 = "13c94b8044c54415e6f04c307f79f5a5a0935afe8240121caef3c805eb194fb5"
SELECTED_SHA256 = "2d59e8ffa579bcb451656cdb0e1a2256d3b5eda3e6214ea5b3fb734d98df7f65"
ALL_IDS = [122465, 127241, 271822, 271823, 287272, 319088, 319553, 332039, 373735, 374007, 404663, 411372]
INCLUDED_IDS = [319088, 319553, 332039, 373735, 374007, 404663, 411372]
EXCLUDED_IDS = [122465, 127241, 271822, 271823, 287272]
FACT_IDS = [f"fact-tabled-oral-question-{api_id}" for api_id in INCLUDED_IDS]
EDM_FACT_IDS = [
    "fact-early-day-motion-62446",
    "fact-early-day-motion-63037",
    "fact-early-day-motion-64576",
    "fact-early-day-motion-65102",
    "fact-early-day-motion-65889",
    "fact-early-day-motion-66149",
]
SECTION_SUMMARY = (
    "Official UK Parliament records identify 90 Commons written questions tabled by "
    "Jeremy Corbyn in the current Parliament, 306 individual Commons Chamber or "
    "Westminster Hall spoken contributions from 17 July 2024 through the fixed "
    "21 July 2026 capture, six Early Day Motions officially tabled by him from "
    "2 September 2024 through 23 June 2026, and seven tabled oral questions from "
    "18 July 2024 through 25 February 2026. Earlier and future records, later "
    "corrections, written statements, committee oral evidence and other adjacent "
    "parliamentary record types remain outside the completed bounded baselines."
)
GAP_SUMMARY = (
    "The fixture covers 90 Commons written questions tabled in the current Parliament, "
    "306 individual Commons Chamber or Westminster Hall spoken contributions by Jeremy "
    "Corbyn from 17 July 2024 through 16 July 2026, six Early Day Motions tabled from "
    "2 September 2024 through 23 June 2026, and seven tabled oral questions from "
    "18 July 2024 through 25 February 2026. Remaining gaps include written questions "
    "and spoken contributions before 4 July 2024, later question updates, future "
    "records and later Hansard corrections, written statements, committee oral "
    "evidence and any future unresolved official records."
)
GAP_NEXT_ACTION = (
    "Open separately authorised lanes for pre-current-Parliament written questions "
    "and spoken contributions, future refreshes, written statements and committee "
    "oral evidence."
)
GAP_NOTES = (
    "The fixed capture reconciled 202 authorised debate rows to 306 unique official "
    "contribution identifiers with zero unresolved records after normalising the "
    "official permalink resolver's site-relative paths to the official Hansard host. "
    "All spoken-contribution source status values remain unspecified because the "
    "payload exposed raw numeric value 2 without an explicit corrected/rolling label. "
    "The fixed oral-question inventory preserves a 12-record member-query universe, "
    "seven current-Parliament inclusions and five pre-current-Parliament exclusions. "
    "Oral-question QuestionType and Status remain numeric because the official payload "
    "did not expose labels. A question asked is recorded only as a question asked."
)


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest(value: Any) -> str:
    return digest_bytes(canonical(value))


def git_output(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout


def member(value: Any) -> Any:
    if value is None:
        return None
    return {
        "mnis_id": value.get("MnisId"),
        "pims_id": value.get("PimsId"),
        "name": value.get("Name"),
        "list_as": value.get("ListAs"),
        "constituency": value.get("Constituency"),
        "status": value.get("Status"),
        "party": value.get("Party"),
        "party_id": value.get("PartyId"),
        "party_colour": value.get("PartyColour"),
        "photo_url": value.get("PhotoUrl"),
    }


def normalise_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "api_id": record.get("Id"),
        "question_type_value": record.get("QuestionType"),
        "question_type_label": None,
        "question_text": record.get("QuestionText"),
        "status_value": record.get("Status"),
        "status_label": None,
        "number": record.get("Number"),
        "tabled_when": record.get("TabledWhen"),
        "removed_from_to_be_asked_when": record.get("RemovedFromToBeAskedWhen"),
        "declarable_interest_detail": record.get("DeclarableInterestDetail"),
        "hansard_link": record.get("HansardLink"),
        "uin": record.get("UIN"),
        "answering_when": record.get("AnsweringWhen"),
        "answering_body_id": record.get("AnsweringBodyId"),
        "answering_body": record.get("AnsweringBody"),
        "answering_minister_title": record.get("AnsweringMinisterTitle"),
        "asking_member": member(record.get("AskingMember")),
        "answering_minister": member(record.get("AnsweringMinister")),
        "asking_member_id": record.get("AskingMemberId"),
        "answering_minister_id": record.get("AnsweringMinisterId"),
    }


def load_inventory() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    packet = json.loads(INVENTORY.read_text(encoding="utf-8"))
    assert packet["inventory_id"] == INVENTORY_ID
    assert packet["schema_version"] == "1"
    assert packet["capture"]["captured_at_utc"] == CAPTURED_AT
    assert packet["capture"]["source"]["official_url"] == OFFICIAL_URL
    assert packet["checksums"] == {
        "canonical_payload_sha256": PACKET_SHA256,
        "gzip_response_sha256": GZIP_SHA256,
        "raw_response_sha256": RAW_SHA256,
    }
    gz = base64.b64decode(packet["capture"]["raw_response_gzip_base64"])
    assert digest_bytes(gz) == GZIP_SHA256
    raw = gzip.decompress(gz)
    assert digest_bytes(raw) == RAW_SHA256
    response = json.loads(raw)
    assert response["StatusCode"] == 200
    assert response["Success"] is True
    assert response["Errors"] == []
    assert response["PagingInfo"] == packet["capture"]["paging"]
    records = [normalise_record(record) for record in response["Response"]]
    assert [record["api_id"] for record in records] == ALL_IDS
    universe = packet["member_query_universe"]
    assert universe["record_count"] == 12
    assert universe["api_ids"] == ALL_IDS
    assert universe["records_sha256"] == digest(records)
    for record in records:
        assert universe["record_sha256"][str(record["api_id"])] == digest(record)
        assert record["asking_member_id"] == 185
        assert record["asking_member"]["mnis_id"] == 185
        assert record["asking_member"]["name"] == "Jeremy Corbyn"
        assert record["question_type_label"] is None
        assert record["status_label"] is None
    selection = packet["current_parliament_selection"]
    assert selection["included_api_ids"] == INCLUDED_IDS
    assert selection["excluded_pre_current_parliament_api_ids"] == EXCLUDED_IDS
    assert selection["accepted_record_count"] == 7
    assert selection["excluded_record_count"] == 5
    selected = [record for record in records if record["api_id"] in INCLUDED_IDS]
    assert [record["api_id"] for record in selected] == INCLUDED_IDS
    assert selection["selected_records_sha256"] == SELECTED_SHA256 == digest(selected)
    payload = {key: value for key, value in packet.items() if key != "checksums"}
    assert digest(payload) == PACKET_SHA256
    return packet, selected


def load_base_fixture() -> dict[str, Any]:
    assert git_output("rev-parse", f"{BASE_COMMIT}:{FIXTURE_REL}").strip() == BASE_FIXTURE_BLOB
    raw = git_output("show", f"{BASE_COMMIT}:{FIXTURE_REL}")
    return json.loads(raw)


def make_source() -> dict[str, Any]:
    return {
        "source_id": SOURCE_ID,
        "title": "Jeremy Corbyn current-Parliament tabled oral questions fixed source inventory",
        "publisher": "UK Parliament",
        "source_type": "parliamentary_record",
        "authority_level": "primary",
        "url": OFFICIAL_URL,
        "repository_path": INVENTORY_REL,
        "server_path": "",
        "publication_date": None,
        "capture_date": "2026-07-23",
        "coverage_from": "2024-07-18",
        "coverage_to": "2026-02-25",
        "checksum": PACKET_SHA256,
        "limitations": (
            "Fixed official member-query capture at 2026-07-23T17:27:27Z. The checksum "
            f"field is the canonical packet payload SHA-256 {PACKET_SHA256}; the "
            f"distinct raw response SHA-256 is {RAW_SHA256}. Numeric QuestionType and "
            "Status values are preserved without inferred labels. Completeness is "
            "bounded to the public API universe at capture time; later records and "
            "corrections are outside this source."
        ),
    }


def make_fact(record: dict[str, Any]) -> dict[str, Any]:
    api_id = record["api_id"]
    assert api_id in INCLUDED_IDS
    raw_question_text = record["question_text"]
    assert isinstance(raw_question_text, str) and raw_question_text.strip()
    question_text = raw_question_text.strip()
    tabled_when = record["tabled_when"]
    answering_when = record["answering_when"]
    uin = record["uin"]
    answering_body = record["answering_body"]
    assert question_text
    assert tabled_when and len(tabled_when) >= 10
    assert uin
    assert answering_body
    tabled_date = tabled_when[:10]
    statement = (
        f"On {tabled_date}, UK Parliament recorded Jeremy Corbyn as tabling oral "
        f"question {uin} (official API ID {api_id}) to {answering_body}: "
        f"“{question_text}”"
    )
    notes_payload = {
        "answering_body": answering_body,
        "answering_body_id": record["answering_body_id"],
        "answering_date": answering_when[:10] if answering_when else None,
        "answering_minister_id": record["answering_minister_id"],
        "answering_minister_title": record["answering_minister_title"],
        "answering_when": answering_when,
        "api_id": api_id,
        "declarable_interest_detail": record["declarable_interest_detail"],
        "hansard_link": record["hansard_link"],
        "neutrality": (
            "A question asked is recorded only as a question asked. It is not evidence "
            "that Jeremy Corbyn adopted the premise, made a commitment, asserted a "
            "position or caused an outcome."
        ),
        "number": record["number"],
        "question_text": raw_question_text,
        "question_type_label": None,
        "question_type_value": record["question_type_value"],
        "removed_from_to_be_asked_when": record["removed_from_to_be_asked_when"],
        "status_label": None,
        "status_value": record["status_value"],
        "tabled_when": tabled_when,
        "uin": uin,
    }
    return {
        "fact_id": f"fact-tabled-oral-question-{api_id}",
        "section_id": "speeches_and_questions",
        "statement": statement,
        "fact_type": "question",
        "date": tabled_date,
        "date_from": None,
        "date_to": None,
        "source_ids": [SOURCE_ID],
        "confidence": "high",
        "evidence_status": "verified",
        "notes": json.dumps(
            notes_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
    }


def build_expected() -> dict[str, Any]:
    _, selected = load_inventory()
    expected = copy.deepcopy(load_base_fixture())
    assert expected["publication"] == {
        "status": "not_ready",
        "human_review_required": True,
        "public_output_authorised": False,
        "approved_by": None,
        "approved_at": None,
        "notes": "Fixture output must not be treated as a public profile.",
    }
    source_ids = [source["source_id"] for source in expected["sources"]]
    fact_ids = [fact["fact_id"] for fact in expected["facts"]]
    assert SOURCE_ID not in source_ids
    assert not set(FACT_IDS) & set(fact_ids)
    expected["sources"].append(make_source())
    new_facts = [make_fact(record) for record in selected]
    assert [fact["fact_id"] for fact in new_facts] == FACT_IDS
    expected["facts"].extend(new_facts)

    section = next(
        section
        for section in expected["sections"]
        if section["section_id"] == "speeches_and_questions"
    )
    assert section["status"] == "partial"
    assert section["claim_ids"] == []
    assert section["interpretation_ids"] == []
    assert section["relationship_ids"] == []
    assert section["fact_ids"][-6:] == EDM_FACT_IDS
    assert len([fact_id for fact_id in section["fact_ids"] if fact_id.startswith("fact-written-question-")]) == 90
    assert len([fact_id for fact_id in section["fact_ids"] if fact_id.startswith("fact-spoken-contribution-")]) == 306
    section["fact_ids"].extend(FACT_IDS)
    section["summary"] = SECTION_SUMMARY

    gap = next(
        gap
        for gap in expected["coverage_gaps"]
        if gap["gap_id"] == "gap-speeches-questions-current-parliament-scope"
    )
    assert gap["section_id"] == "speeches_and_questions"
    assert gap["status"] == "open"
    assert gap["blocks_publication"] is True
    gap["summary"] = GAP_SUMMARY
    gap["date_to"] = "2026-07-23"
    gap["next_action"] = GAP_NEXT_ACTION
    gap["notes"] = GAP_NOTES

    assert [source["source_id"] for source in expected["sources"]].count(SOURCE_ID) == 1
    assert [fact["fact_id"] for fact in expected["facts"]][-7:] == FACT_IDS
    assert section["fact_ids"][-7:] == FACT_IDS
    for collection_name in ("claims", "interpretations", "relationships"):
        collection = expected[collection_name]
        assert all(
            not set(FACT_IDS) & set(item.get("fact_ids", []))
            for item in collection
        )
        assert all(
            SOURCE_ID not in item.get("source_ids", [])
            for item in collection
        )
    assert [
        fact["fact_id"]
        for fact in expected["facts"]
        if SOURCE_ID in fact.get("source_ids", [])
    ] == FACT_IDS
    assert expected["publication"]["status"] == "not_ready"
    assert expected["publication"]["human_review_required"] is True
    assert expected["publication"]["public_output_authorised"] is False
    return expected


def validate_actual(expected: dict[str, Any]) -> None:
    actual = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert actual == expected, "fixture differs from the deterministic authorised integration"
    source = next(source for source in actual["sources"] if source["source_id"] == SOURCE_ID)
    assert source["checksum"] == PACKET_SHA256
    assert RAW_SHA256 in source["limitations"]
    facts = [fact for fact in actual["facts"] if fact["fact_id"] in FACT_IDS]
    assert [fact["fact_id"] for fact in facts] == FACT_IDS
    assert all(fact["fact_type"] == "question" for fact in facts)
    assert all(fact["section_id"] == "speeches_and_questions" for fact in facts)
    assert all(fact["source_ids"] == [SOURCE_ID] for fact in facts)
    assert all(fact["confidence"] == "high" for fact in facts)
    assert all(fact["evidence_status"] == "verified" for fact in facts)
    forbidden = (
        "commitment",
        "public position",
        "ideology",
        "motive",
        "importance",
        "influence",
        "effectiveness",
        "outcome",
        "wrongdoing",
        "delivery",
        "fulfilment",
        "broken promise",
        "contradiction",
    )
    added_text = "\n".join(
        [source["title"], source["limitations"]]
        + [fact["statement"] + "\n" + fact["notes"] for fact in facts]
    ).lower()
    assert "not evidence that jeremy corbyn adopted the premise" in added_text
    for phrase in forbidden:
        if phrase in {"commitment", "public position", "outcome"}:
            continue
        assert phrase not in added_text, phrase


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build-output",
        type=Path,
        help="Write the deterministic authorised fixture to this path.",
    )
    args = parser.parse_args()
    assert git_output("rev-parse", f"HEAD:{INVENTORY_REL}").strip() == INVENTORY_BLOB
    expected = build_expected()
    if args.build_output:
        args.build_output.parent.mkdir(parents=True, exist_ok=True)
        args.build_output.write_text(
            json.dumps(expected, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"BUILT: {args.build_output}")
        return 0
    validate_actual(expected)
    print("PASS: seven neutral tabled oral questions are integrated deterministically")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
