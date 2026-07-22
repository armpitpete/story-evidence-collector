#!/usr/bin/env python3
"""Validate the fixed Jeremy Corbyn current-Parliament EDM source inventory.

The default run is deterministic and offline. ``--live`` replays the exact
supported UK Parliament Early Day Motions API query and all six detail records.
All live requests are read-only.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "research/complete-mp-reports/jeremy-corbyn/current-parliament-early-day-motions-source-inventory-v1.json"
NOTE_PATH = ROOT / "docs/jeremy-corbyn-current-parliament-early-day-motions-source-note-v1.md"
EXPECTED_INVENTORY_ID = "jeremy-corbyn-current-parliament-early-day-motions-source-inventory-v1"
EXPECTED_MEMBER_ID = 185
EXPECTED_IDS = {62446, 63037, 64576, 65102, 65889, 66149}
EXPECTED_RECORD_IDS = {f"edm-{value}" for value in EXPECTED_IDS}
ALLOWED_TOP_LEVEL_KEYS = {
    "schema_version", "inventory_id", "capture", "result_page_snapshot",
    "motions", "coverage", "capture_sha256",
}
FORBIDDEN_INTERPRETIVE_KEYS = {
    "topic", "ideology", "sentiment", "personality", "motive",
    "commitment", "public_position", "delivery", "fulfilment",
    "broken_promise", "reversal", "contradiction", "consistency",
    "hypocrisy", "importance", "influence", "effectiveness", "success",
    "legality", "propriety", "relationship", "publication_authorised",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing required file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    raise AssertionError("unreachable")


def walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(key)
            keys.update(walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(walk_keys(child))
    return keys


def iso_date(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        fail(f"{label} must be an ISO date: {value!r}")
    raise AssertionError("unreachable")


def validate_hash(value: dict[str, Any], hash_key: str, label: str) -> None:
    supplied = value.get(hash_key)
    if not isinstance(supplied, str) or len(supplied) != 64:
        fail(f"{label} missing SHA-256")
    unhashed = copy.deepcopy(value)
    del unhashed[hash_key]
    if sha256_value(unhashed) != supplied:
        fail(f"{label} checksum mismatch")


def validate_fixed_packet(packet: dict[str, Any]) -> None:
    if set(packet) != ALLOWED_TOP_LEVEL_KEYS:
        fail(f"unexpected top-level keys: {sorted(set(packet) ^ ALLOWED_TOP_LEVEL_KEYS)}")
    if packet["schema_version"] != "1" or packet["inventory_id"] != EXPECTED_INVENTORY_ID:
        fail("fixed inventory identity changed")
    validate_hash(packet, "capture_sha256", "capture")
    forbidden = walk_keys(packet) & FORBIDDEN_INTERPRETIVE_KEYS
    if forbidden:
        fail(f"interpretive keys are forbidden: {sorted(forbidden)}")

    capture = packet["capture"]
    query = capture["query"]
    member = capture["member"]
    if member != {"member_id": "185", "display_name": "Jeremy Corbyn", "constituency": "Islington North"}:
        fail("member identity changed")
    if capture["parliament_start_date"] != "2024-07-04" or capture["capture_end_date"] != "2026-07-22":
        fail("authorised date boundary changed")
    datetime.fromisoformat(capture["captured_at_utc"].replace("Z", "+00:00"))
    if query["tabled_from"] != "2024-07-04" or query["tabled_to"] != "2026-07-22":
        fail("query date boundary changed")
    if query["include_signed_by_member"] is not False or query["include_withdrawn_motions"] is not True:
        fail("member-role or withdrawn-motion completeness boundary changed")
    if query["show_prayers_only"] is not False:
        fail("query must not restrict the inventory to prayers")
    if (query["result_total"], query["page_count"], query["pagination_complete"]) != (6, 1, True):
        fail("fixed result count or pagination proof changed")
    if (query["api_skip"], query["api_take"], query["api_total"]) != (0, 100, 6):
        fail("official API pagination boundary changed")
    api_url = query["official_api_url"]
    for required in (
        "parameters.memberId=185", "parameters.includeSponsoredByMember=false",
        "parameters.tabledStartDate=2024-07-04", "parameters.tabledEndDate=2026-07-22",
        "parameters.statuses=Published", "parameters.statuses=Withdrawn",
        "parameters.skip=0", "parameters.take=100",
    ):
        if required not in api_url:
            fail(f"official API query missing exact parameter: {required}")

    result = packet["result_page_snapshot"]
    validate_hash(result, "extract_sha256", "result-page extract")
    if result["official_api_url"] != api_url:
        fail("result-page API URL differs from fixed query")
    if (result["api_skip"], result["api_take"], result["api_total"], result["api_global_total"]) != (0, 100, 6, 6):
        fail("fixed API result totals changed")
    if result["total_results"] != len(result["records"]) or result["total_results"] != 6:
        fail("result-page count does not reconcile")

    motions = packet["motions"]
    if len(motions) != 6:
        fail("fixed inventory must contain exactly six motions")
    if {row["record_id"] for row in motions} != EXPECTED_RECORD_IDS:
        fail("stable record ID set changed")
    if {row["official_motion_id"] for row in motions} != EXPECTED_IDS:
        fail("official motion ID set changed")
    if len({row["record_id"] for row in motions}) != 6 or len({row["official_url"] for row in motions}) != 6:
        fail("duplicate stable IDs or official URLs")

    capture_end = iso_date(capture["capture_end_date"], "capture_end_date")
    by_id = {row["official_motion_id"]: row for row in motions}
    for row in motions:
        validate_hash(row, "detail_extract_sha256", row["record_id"])
        motion_id = row["official_motion_id"]
        if row["record_id"] != f"edm-{motion_id}":
            fail(f"unstable record ID for {motion_id}")
        tabled = iso_date(row["tabled_date"], f"{row['record_id']} tabled_date")
        if not date(2024, 7, 4) <= tabled <= capture_end:
            fail(f"{row['record_id']} lies outside the authorised date range")
        if row["session"] not in {"2024-26", "2026-27"}:
            fail(f"unexpected session for {row['record_id']}")
        if row["official_api_url"] != f"https://oralquestionsandmotions-api.parliament.uk/EarlyDayMotion/{motion_id}":
            fail(f"official API detail URL changed for {row['record_id']}")
        if row["official_status_code"] != 0 or row["api_amendment_to_motion_id"] is not None:
            fail(f"raw official status/amendment boundary changed for {row['record_id']}")
        if row["api_praying_against_negative_statutory_instrument_id"] is not None:
            fail(f"unexpected prayer instrument link for {row['record_id']}")
        if row["record_kind_label"] != "EDM (Early Day Motion)" or not row["title"].strip() or not row["motion_text"].strip():
            fail(f"required source-explicit text missing for {row['record_id']}")
        sponsor = row["primary_sponsor"]
        if sponsor["member_id"] != "185" or sponsor["display_name"] != "Corbyn, Jeremy" or sponsor["primary_label"] != "Primary":
            fail(f"explicit primary sponsor changed for {row['record_id']}")
        if sponsor["constituency_as_displayed"] != "Islington North":
            fail(f"constituency changed for {row['record_id']}")
        iso_date(sponsor["signed_date"], f"{row['record_id']} signed_date")
        signatures = row["signature_snapshot"]
        if signatures["total"] != signatures["supporters"] + signatures["withdrawn"]:
            fail(f"signature snapshot does not reconcile for {row['record_id']}")
        if row["motion_withdrawn"] is not None or row["is_prayer"] is not None:
            fail(f"unlabelled page fields must remain unresolved for {row['record_id']}")
        if row["unresolved_fields"] != ["motion_withdrawn", "is_prayer"]:
            fail(f"unresolved field boundary changed for {row['record_id']}")

    result_ids = [row["official_motion_id"] for row in result["records"]]
    if set(result_ids) != EXPECTED_IDS or len(result_ids) != len(set(result_ids)):
        fail("result-page records do not reconcile to fixed details")
    for summary in result["records"]:
        detail = by_id[summary["official_motion_id"]]
        for key in ("edm_number", "edm_suffix", "title", "tabled_date", "official_url"):
            if summary[key] != detail[key]:
                fail(f"result/detail mismatch for {detail['record_id']}: {key}")
        if summary["tabled_by"] != "Jeremy Corbyn":
            fail(f"result row is not tabled by Jeremy Corbyn: {detail['record_id']}")
        if summary["signature_count_snapshot"] != detail["signature_snapshot"]["total"]:
            fail(f"signature snapshot mismatch for {detail['record_id']}")

    expected_coverage = {
        "accepted_records": 6,
        "sessions": ["2024-26", "2026-27"],
        "earliest_tabled_date": "2024-09-02",
        "latest_tabled_date": "2026-06-23",
        "duplicate_record_ids": 0,
        "duplicate_official_motion_ids": 0,
        "duplicate_official_urls": 0,
        "motions_merely_signed_excluded": True,
        "pre_current_parliament_excluded": True,
        "canonical_fixture_integration": False,
    }
    if packet["coverage"] != expected_coverage:
        fail("coverage proof changed")

    note = NOTE_PATH.read_text(encoding="utf-8")
    for required in (EXPECTED_INVENTORY_ID, packet["capture_sha256"], api_url, capture["captured_at_utc"], "six", "No canonical fixture"):
        if required not in note:
            fail(f"source note missing required value: {required}")
    for row in motions:
        if row["official_url"] not in note or row["official_api_url"] not in note or row["detail_extract_sha256"] not in note:
            fail(f"source note does not reconcile {row['record_id']}")


def fetch_json(url: str, attempts: int = 3) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(request, timeout=30) as response:
                if response.status != 200:
                    fail(f"official API returned HTTP {response.status}: {url}")
                return json.loads(response.read().decode(response.headers.get_content_charset() or "utf-8"))
        except Exception as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(attempt)
    fail(f"failed to fetch official API after {attempts} attempts: {url}: {last_error}")
    raise AssertionError("unreachable")


def value_date(value: str) -> str:
    return value[:10]


def validate_api_motion(api: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    sponsor = api["PrimarySponsor"]
    comparisons = {
        "Id": expected["official_motion_id"],
        "Status": expected["official_status_code"],
        "MemberId": EXPECTED_MEMBER_ID,
        "Title": expected["title"],
        "MotionText": expected["motion_text"],
        "AmendmentToMotionId": expected["api_amendment_to_motion_id"],
        "UIN": int(expected["edm_number"]),
        "AmendmentSuffix": expected["edm_suffix"],
        "PrayingAgainstNegativeStatutoryInstrumentId": expected["api_praying_against_negative_statutory_instrument_id"],
        "SponsorsCount": expected["signature_snapshot"]["total"],
    }
    for key, value in comparisons.items():
        if api.get(key) != value:
            fail(f"{label} API field changed: {key}: expected {value!r}, got {api.get(key)!r}")
    if value_date(api["DateTabled"]) != expected["tabled_date"]:
        fail(f"{label} tabled date changed")
    sponsor_expected = expected["primary_sponsor"]
    for key, value in {
        "MnisId": EXPECTED_MEMBER_ID,
        "Name": "Jeremy Corbyn",
        "ListAs": sponsor_expected["display_name"],
        "Constituency": sponsor_expected["constituency_as_displayed"],
        "Party": sponsor_expected["party_as_displayed"],
    }.items():
        if sponsor.get(key) != value:
            fail(f"{label} primary sponsor field changed: {key}")


def validate_live_sources(packet: dict[str, Any]) -> None:
    query = packet["capture"]["query"]
    payload = fetch_json(query["official_api_url"])
    if payload.get("Success") is not True or payload.get("StatusCode") != 200 or payload.get("Errors") != []:
        fail("official list API did not return a clean success response")
    paging = payload.get("PagingInfo") or {}
    if (paging.get("Skip"), paging.get("Take"), paging.get("Total"), paging.get("GlobalTotal")) != (0, 100, 6, 6):
        fail(f"official list API pagination changed: {paging}")
    rows = payload.get("Response") or []
    if len(rows) != 6 or {row.get("Id") for row in rows} != EXPECTED_IDS:
        fail(f"official list API record set changed: {[row.get('Id') for row in rows]}")

    expected_by_id = {row["official_motion_id"]: row for row in packet["motions"]}
    for api_row in rows:
        expected = expected_by_id[api_row["Id"]]
        validate_api_motion(api_row, expected, expected["record_id"])
        detail_payload = fetch_json(expected["official_api_url"])
        if detail_payload.get("Success") is not True or detail_payload.get("StatusCode") != 200 or detail_payload.get("Errors") != []:
            fail(f"official detail API did not return clean success for {expected['record_id']}")
        detail = detail_payload.get("Response") or {}
        detail_for_compare = copy.deepcopy(detail)
        detail_for_compare["SponsorsCount"] = expected["signature_snapshot"]["total"]
        validate_api_motion(detail_for_compare, expected, f"{expected['record_id']} detail")
        sponsors = detail.get("Sponsors") or []
        sig = expected["signature_snapshot"]
        if len(sponsors) != sig["total"]:
            fail(f"detail sponsor count changed for {expected['record_id']}")
        withdrawn = [row for row in sponsors if row.get("IsWithdrawn") is True]
        supporters = [row for row in sponsors if row.get("IsWithdrawn") is False]
        if (len(supporters), len(withdrawn)) != (sig["supporters"], sig["withdrawn"]):
            fail(f"detail signature split changed for {expected['record_id']}")
        primary = [row for row in sponsors if row.get("MemberId") == EXPECTED_MEMBER_ID and row.get("SponsoringOrder") == 1]
        if len(primary) != 1 or primary[0].get("IsWithdrawn") is not False:
            fail(f"explicit primary sponsor missing or withdrawn for {expected['record_id']}")
        if value_date(primary[0]["CreatedWhen"]) != expected["primary_sponsor"]["signed_date"]:
            fail(f"primary sponsor date changed for {expected['record_id']}")
        if detail.get("Amendments") != []:
            fail(f"amendment set changed for {expected['record_id']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="replay supported official UK Parliament API endpoints")
    args = parser.parse_args()
    packet = load_json(PACKET_PATH)
    validate_fixed_packet(packet)
    print("PASS: fixed six-record current-Parliament EDM inventory is canonical and internally complete")
    if args.live:
        validate_live_sources(packet)
        print("PASS: official filtered list API and all six detail endpoints match the fixed capture")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
