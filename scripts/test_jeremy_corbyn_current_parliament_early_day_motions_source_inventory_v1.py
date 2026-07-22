#!/usr/bin/env python3
"""Validate the fixed Jeremy Corbyn current-Parliament EDM source inventory.

The default run is fully deterministic and offline. ``--live`` additionally
replays the exact official UK Parliament search and detail-page interface used
for the fixed capture. The live probe is deliberately read-only.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import re
import sys
import time
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "research/complete-mp-reports/jeremy-corbyn/current-parliament-early-day-motions-source-inventory-v1.json"
NOTE_PATH = ROOT / "docs/jeremy-corbyn-current-parliament-early-day-motions-source-note-v1.md"
EXPECTED_INVENTORY_ID = "jeremy-corbyn-current-parliament-early-day-motions-source-inventory-v1"
EXPECTED_MEMBER_ID = "185"
EXPECTED_RECORD_IDS = {
    "edm-62446",
    "edm-63037",
    "edm-64576",
    "edm-65102",
    "edm-65889",
    "edm-66149",
}
EXPECTED_OFFICIAL_IDS = {62446, 63037, 64576, 65102, 65889, 66149}
ALLOWED_TOP_LEVEL_KEYS = {
    "schema_version",
    "inventory_id",
    "capture",
    "result_page_snapshot",
    "motions",
    "coverage",
    "capture_sha256",
}
FORBIDDEN_INTERPRETIVE_KEYS = {
    "topic",
    "ideology",
    "sentiment",
    "personality",
    "motive",
    "commitment",
    "public_position",
    "delivery",
    "fulfilment",
    "broken_promise",
    "reversal",
    "contradiction",
    "consistency",
    "hypocrisy",
    "importance",
    "influence",
    "effectiveness",
    "success",
    "legality",
    "propriety",
    "relationship",
    "publication_authorised",
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


def require_iso_date(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        fail(f"{label} must be an ISO date: {value!r}")
    raise AssertionError("unreachable")


def validate_fixed_packet(packet: dict[str, Any]) -> None:
    if set(packet) != ALLOWED_TOP_LEVEL_KEYS:
        fail(f"unexpected top-level keys: {sorted(set(packet) ^ ALLOWED_TOP_LEVEL_KEYS)}")
    if packet["schema_version"] != "1":
        fail("schema_version must remain 1")
    if packet["inventory_id"] != EXPECTED_INVENTORY_ID:
        fail("unexpected inventory_id")

    supplied_capture_hash = packet["capture_sha256"]
    unhashed_packet = copy.deepcopy(packet)
    del unhashed_packet["capture_sha256"]
    if sha256_value(unhashed_packet) != supplied_capture_hash:
        fail("capture_sha256 does not match canonical packet content")

    forbidden = walk_keys(packet) & FORBIDDEN_INTERPRETIVE_KEYS
    if forbidden:
        fail(f"interpretive keys are forbidden in this source inventory: {sorted(forbidden)}")

    capture = packet["capture"]
    member = capture["member"]
    query = capture["query"]
    if member["member_id"] != EXPECTED_MEMBER_ID or member["display_name"] != "Jeremy Corbyn":
        fail("capture member identity changed")
    if capture["parliament_start_date"] != "2024-07-04":
        fail("current-Parliament boundary changed")
    capture_end = require_iso_date(capture["capture_end_date"], "capture_end_date")
    require_iso_date(capture["parliament_start_date"], "parliament_start_date")
    datetime.fromisoformat(capture["captured_at_utc"].replace("Z", "+00:00"))

    if query["tabled_from"] != "2024-07-04" or query["tabled_to"] != capture["capture_end_date"]:
        fail("query date boundary does not match capture boundary")
    if query["include_signed_by_member"] is not False:
        fail("motions merely signed by the member must remain excluded")
    if query["include_withdrawn_motions"] is not True:
        fail("the completeness query must include withdrawn motions")
    if query["show_prayers_only"] is not False:
        fail("the completeness query must not restrict the inventory to prayers")
    if query["result_total"] != 6 or query["page_count"] != 1 or query["pagination_complete"] is not True:
        fail("fixed query count or pagination proof changed")
    if "MemberId=185" not in query["official_url"] or "IncludeWithdrawn=true" not in query["official_url"]:
        fail("official query URL lost its exact member or withdrawn-motion boundary")

    result_page = packet["result_page_snapshot"]
    supplied_result_hash = result_page["extract_sha256"]
    unhashed_result = copy.deepcopy(result_page)
    del unhashed_result["extract_sha256"]
    if sha256_value(unhashed_result) != supplied_result_hash:
        fail("result-page extract checksum mismatch")
    if result_page["official_url"] != query["official_url"]:
        fail("result-page URL differs from fixed query URL")
    if result_page["page_number"] != 1 or result_page["page_count"] != 1:
        fail("result-page pagination metadata changed")
    if result_page["total_results"] != len(result_page["records"]) or result_page["total_results"] != 6:
        fail("result-page total does not match captured records")

    motions = packet["motions"]
    if len(motions) != 6:
        fail("the fixed source inventory must contain exactly six records")
    record_ids = [row["record_id"] for row in motions]
    official_ids = [row["official_motion_id"] for row in motions]
    urls = [row["official_url"] for row in motions]
    if set(record_ids) != EXPECTED_RECORD_IDS or len(record_ids) != len(set(record_ids)):
        fail("record IDs are missing, duplicated or unexpected")
    if set(official_ids) != EXPECTED_OFFICIAL_IDS or len(official_ids) != len(set(official_ids)):
        fail("official motion IDs are missing, duplicated or unexpected")
    if len(urls) != len(set(urls)):
        fail("official motion URLs must be unique")

    for row in motions:
        supplied_detail_hash = row["detail_extract_sha256"]
        unhashed_row = copy.deepcopy(row)
        del unhashed_row["detail_extract_sha256"]
        if sha256_value(unhashed_row) != supplied_detail_hash:
            fail(f"detail extract checksum mismatch for {row['record_id']}")
        if row["record_id"] != f"edm-{row['official_motion_id']}":
            fail(f"unstable record ID for official motion {row['official_motion_id']}")
        tabled = require_iso_date(row["tabled_date"], f"{row['record_id']} tabled_date")
        if tabled < date(2024, 7, 4) or tabled > capture_end:
            fail(f"{row['record_id']} lies outside the authorised date boundary")
        if row["session"] not in {"2024-26", "2026-27"}:
            fail(f"unexpected session for {row['record_id']}")
        if row["record_kind_label"] != "EDM (Early Day Motion)":
            fail(f"record kind is not source-explicit for {row['record_id']}")
        if not row["title"].strip() or not row["motion_text"].strip():
            fail(f"title or full official text missing for {row['record_id']}")
        sponsor = row["primary_sponsor"]
        if sponsor["member_id"] != EXPECTED_MEMBER_ID:
            fail(f"wrong primary sponsor member ID for {row['record_id']}")
        if sponsor["display_name"] != "Corbyn, Jeremy" or sponsor["primary_label"] != "Primary":
            fail(f"Jeremy Corbyn is not preserved as explicit primary sponsor for {row['record_id']}")
        if sponsor["constituency_as_displayed"] != "Islington North":
            fail(f"constituency changed for {row['record_id']}")
        require_iso_date(sponsor["signed_date"], f"{row['record_id']} primary signed_date")
        sig = row["signature_snapshot"]
        if sig["total"] != sig["supporters"] + sig["withdrawn"]:
            fail(f"signature snapshot does not reconcile for {row['record_id']}")
        if row["motion_withdrawn"] is not None or row["is_prayer"] is not None:
            fail(f"unexposed motion/prayer status must remain unresolved for {row['record_id']}")
        if row["unresolved_fields"] != ["motion_withdrawn", "is_prayer"]:
            fail(f"unresolved field boundary changed for {row['record_id']}")
        if row["official_status_labels"] != []:
            fail(f"no separate official status labels were displayed for {row['record_id']}")

    result_ids = [row["official_motion_id"] for row in result_page["records"]]
    if set(result_ids) != EXPECTED_OFFICIAL_IDS or len(result_ids) != len(set(result_ids)):
        fail("result-page IDs do not reconcile to detail records")
    detail_by_id = {row["official_motion_id"]: row for row in motions}
    for summary in result_page["records"]:
        detail = detail_by_id[summary["official_motion_id"]]
        for key in ("edm_number", "edm_suffix", "title", "tabled_date", "official_url"):
            if summary[key] != detail[key]:
                fail(f"result/detail mismatch for {detail['record_id']}: {key}")
        if summary["tabled_by"] != "Jeremy Corbyn":
            fail(f"result row is not tabled by Jeremy Corbyn: {detail['record_id']}")
        if summary["signature_count_snapshot"] != detail["signature_snapshot"]["total"]:
            fail(f"result/detail signature mismatch for {detail['record_id']}")

    coverage = packet["coverage"]
    if coverage != {
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
    }:
        fail("coverage proof changed")

    note = NOTE_PATH.read_text(encoding="utf-8")
    for required in (
        EXPECTED_INVENTORY_ID,
        supplied_capture_hash,
        capture["captured_at_utc"],
        "six",
        "No canonical fixture",
    ):
        if required not in note:
            fail(f"source note missing required value: {required}")
    for row in motions:
        if row["official_url"] not in note or row["detail_extract_sha256"] not in note:
            fail(f"source note does not reconcile {row['record_id']}")


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.motion_links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href and re.match(r"^/early-day-motion/\d+(?:/[^?#\"]*)?$", href):
            self.motion_links.append(href)


def strip_markup(raw: str) -> str:
    without_scripts = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"(?s)<[^>]+>", " ", without_scripts))).strip()


def parse_h1(raw: str) -> str:
    match = re.search(r"(?is)<h1\b[^>]*>(.*?)</h1>", raw)
    if not match:
        fail("official detail page has no h1")
    return strip_markup(match.group(1))


def fetch_html(url: str, attempts: int = 3) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "story-evidence-collector/1.0 (+https://github.com/armpitpete/story-evidence-collector)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(request, timeout=30) as response:
                body = response.read()
                content_type = response.headers.get_content_type()
                if response.status != 200:
                    fail(f"official source returned HTTP {response.status}: {url}")
                if content_type not in {"text/html", "application/xhtml+xml"}:
                    fail(f"unexpected official content type {content_type!r}: {url}")
                return body.decode(response.headers.get_content_charset() or "utf-8")
        except Exception as exc:  # network failures need a concise final diagnostic
            last_error = exc
            if attempt < attempts:
                time.sleep(attempt)
    fail(f"failed to fetch official source after {attempts} attempts: {url}: {last_error}")
    raise AssertionError("unreachable")


def replace_page(url: str, page: int) -> str:
    split = urlsplit(url)
    pairs = parse_qsl(split.query, keep_blank_values=True)
    replaced = False
    updated: list[tuple[str, str]] = []
    for key, value in pairs:
        if key.lower() == "page":
            updated.append((key, str(page)))
            replaced = True
        else:
            updated.append((key, value))
    if not replaced:
        updated.append(("page", str(page)))
    return urlunsplit((split.scheme, split.netloc, split.path, urlencode(updated), split.fragment))


def parse_result_page(raw: str, base_url: str) -> tuple[int, int, int, list[str]]:
    flat = strip_markup(raw)
    match = re.search(r"Total results\s+(\d+)\s+\(page\s+(\d+)\s+of\s+(\d+)\)", flat, re.I)
    if not match:
        fail("official result page did not expose total/page pagination text")
    total, page, page_count = (int(part) for part in match.groups())
    parser = LinkParser()
    parser.feed(raw)
    links: list[str] = []
    seen: set[str] = set()
    for href in parser.motion_links:
        absolute = urljoin(base_url, href)
        if absolute not in seen:
            links.append(absolute)
            seen.add(absolute)
    return total, page, page_count, links


def parse_uk_date(value: str) -> str:
    return datetime.strptime(value.strip(), "%d %B %Y").date().isoformat()


def parse_detail_page(raw: str, url: str) -> dict[str, Any]:
    flat = strip_markup(raw)
    title = parse_h1(raw)
    header = re.search(
        r"EDM \(Early Day Motion\)\s+([0-9]+(?:A[0-9]+)?):\s+tabled on\s+(\d{1,2} [A-Za-z]+ \d{4})",
        flat,
        re.I,
    )
    if not header:
        fail(f"official EDM number/date missing: {url}")
    edm_token, tabled_text = header.groups()
    edm_number_match = re.fullmatch(r"(\d+)(A\d+)?", edm_token, re.I)
    if not edm_number_match:
        fail(f"unparseable official EDM token: {edm_token}")
    session_match = re.search(r"Tabled in the\s+([0-9]{4}-[0-9]{2})\s+session", flat, re.I)
    if not session_match:
        fail(f"official session label missing: {url}")
    motion_match = re.search(r"Motion text\s+(.*?)\s+Signatures\s*\(\d+\)", flat, re.I)
    if not motion_match:
        fail(f"full official motion text missing: {url}")
    total_match = re.search(r"Signatures\s*\((\d+)\)", flat, re.I)
    supporters_match = re.search(r"Supporters\s*\((\d+)\)", flat, re.I)
    withdrawn_match = re.search(r"Withdrawn signatures\s*\((\d+)\)", flat, re.I)
    if not (total_match and supporters_match and withdrawn_match):
        fail(f"signature snapshot fields missing: {url}")
    primary_match = re.search(
        r"Corbyn, Jeremy\s+(.+?)\s+Signed on\s+(\d{1,2} [A-Za-z]+ \d{4})\s+Islington North\s+Primary",
        flat,
        re.I,
    )
    if not primary_match:
        fail(f"Jeremy Corbyn is not displayed as primary sponsor: {url}")
    party, signed_text = primary_match.groups()
    motion_id_match = re.search(r"/early-day-motion/(\d+)", url)
    if not motion_id_match:
        fail(f"official motion ID missing from URL: {url}")
    signed_summary = re.search(r"This motion has been signed by\s+(\d+)\s+Members", flat, re.I)
    if not signed_summary:
        fail(f"signed-member summary missing: {url}")
    no_amendments = bool(re.search(r"It has not yet had any amendments submitted", flat, re.I))
    return {
        "official_motion_id": int(motion_id_match.group(1)),
        "edm_number": edm_number_match.group(1),
        "edm_suffix": edm_number_match.group(2),
        "title": title,
        "tabled_date": parse_uk_date(tabled_text),
        "session": session_match.group(1),
        "motion_text": motion_match.group(1).strip(),
        "primary_party": party.strip(),
        "primary_signed_date": parse_uk_date(signed_text),
        "signature_snapshot": {
            "total": int(total_match.group(1)),
            "supporters": int(supporters_match.group(1)),
            "withdrawn": int(withdrawn_match.group(1)),
        },
        "signed_summary_total": int(signed_summary.group(1)),
        "no_amendments": no_amendments,
    }


def validate_live_sources(packet: dict[str, Any]) -> None:
    query_url = packet["capture"]["query"]["official_url"]
    first_html = fetch_html(query_url)
    total, page, page_count, first_links = parse_result_page(first_html, query_url)
    if page != 1:
        fail(f"official source returned unexpected first page number: {page}")
    links = list(first_links)
    for page_number in range(2, page_count + 1):
        page_url = replace_page(query_url, page_number)
        page_html = fetch_html(page_url)
        page_total, actual_page, actual_page_count, page_links = parse_result_page(page_html, page_url)
        if page_total != total or actual_page != page_number or actual_page_count != page_count:
            fail(f"pagination metadata changed on page {page_number}")
        links.extend(page_links)
    unique_links = list(dict.fromkeys(links))
    live_ids = {
        int(match.group(1))
        for link in unique_links
        if (match := re.search(r"/early-day-motion/(\d+)", link))
    }
    if total != 6 or page_count != 1:
        fail(f"official fixed query now reports {total} results across {page_count} pages; expected 6 across 1")
    if live_ids != EXPECTED_OFFICIAL_IDS:
        fail(f"official fixed query record set changed: expected {sorted(EXPECTED_OFFICIAL_IDS)}, got {sorted(live_ids)}")
    if len(unique_links) != total:
        fail(f"pagination/link completeness failed: total={total}, unique links={len(unique_links)}")

    expected_by_id = {row["official_motion_id"]: row for row in packet["motions"]}
    for motion_id in sorted(EXPECTED_OFFICIAL_IDS):
        expected = expected_by_id[motion_id]
        live = parse_detail_page(fetch_html(expected["official_url"]), expected["official_url"])
        stable_fields = {
            "official_motion_id": expected["official_motion_id"],
            "edm_number": expected["edm_number"],
            "edm_suffix": expected["edm_suffix"],
            "title": expected["title"],
            "tabled_date": expected["tabled_date"],
            "session": expected["session"],
            "motion_text": expected["motion_text"],
            "primary_party": expected["primary_sponsor"]["party_as_displayed"],
            "primary_signed_date": expected["primary_sponsor"]["signed_date"],
            "signature_snapshot": expected["signature_snapshot"],
            "signed_summary_total": expected["signature_snapshot"]["total"],
            "no_amendments": True,
        }
        if live != stable_fields:
            differences = {
                key: {"expected": stable_fields[key], "live": live.get(key)}
                for key in stable_fields
                if live.get(key) != stable_fields[key]
            }
            fail(f"official detail snapshot changed for edm-{motion_id}: {json.dumps(differences, ensure_ascii=False, sort_keys=True)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="replay the exact official UK Parliament interface")
    args = parser.parse_args()
    packet = load_json(PACKET_PATH)
    validate_fixed_packet(packet)
    print("PASS: fixed six-record current-Parliament EDM source inventory is canonical and internally complete")
    if args.live:
        validate_live_sources(packet)
        print("PASS: official member/date/withdrawn query and all six detail pages match the fixed capture")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
